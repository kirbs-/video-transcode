#!/home/kirby/.pyenv/versions/3.7.2/envs/video-transcode/bin/python
from celery import Celery
import subprocess
import sys
# import json
import os
import logging
from celery.task.control import inspect
from datetime import datetime, timedelta
import pendulum
import pathlib
# import shlex
import re
import yaml
import pkg_resources
import argparse
import logging


logging.basicConfig(level=logging.WARN)


# Load config.yaml
# if no env var use package default.
if os.environ.get('VIDEO_TRANSCODE_CONFIG'):
    CONFIG_FILE = os.environ.get('VIDEO_TRANSCODE_CONFIG')
else:
    CONFIG_FILE = pkg_resources.resource_filename('video_transcode','config/config.yaml')

with open(CONFIG_FILE) as f:
    config = yaml.full_load(f.read())
    # os.environ['FFMPEG_BINARY'] = config['FFMPEG_BINARY_PATH']
    os.environ['LD_LIBRARY_PATH'] = '/usr/local/cuda/lib64'


# setup argument parser
parser = argparse.ArgumentParser()

parser.add_argument('filename',
                    nargs='+')
parser.add_argument("-a", "--action",
                    help="ENVIRONMENT should be 'nonprod', 'dev' or 'sqa' and correspond to the AWS account to which you want to deploy.",
                    default=config['DEFAULT_ACTION'])
parser.add_argument("-n", "--now",
                    action='store_true',
                    help="Run action now, don't schedule.")
# parser.add_argument('--add',
#                     action='store_true',
#                     help="Add files to queue. This takes the first arguement as an input in to pathlib.Path.glob.")


logging.debug(f"Transcode mode = {os.environ.get('VIDEO_TRANSCODE_MODE')}")
if os.environ.get('VIDEO_TRANSCODE_MODE'):
    os.environ['FFMPEG_BINARY'] = config['FFMPEG_BINARY_PATH']
    app = Celery(config['CELERY_QUEUE'], broker=config['CONTAINER_CELERY_BROKER'], backend=config['CONTAINER_CELERY_RESULT_BACKEND'])
else:
    app = Celery(config['CELERY_QUEUE'], broker=config['CELERY_BROKER'], backend=config['CELERY_RESULT_BACKEND'])

# import moviepy after setting FFMPEG_BINARY
import moviepy.editor as me


# update celery task visibiity_timeout to 1 week. 
app.conf.update(
    broker_transport_options = {'visibility_timeout': 604800}	
)


def translate_filenames(input_file):
    """Derives file path from video file's base name.

    Plex records shows in a temp location then moves the file into a libary upon completion. It's this 
    temp file's path that is passed to post processing scripts. Since video-transcode time shifts transcoding,
    the temp file path Plex sends isn't valid when video-transcode opens the file.

    Args:
        input_file (str): Path to file to transcode.

    Returns:
        tuple: (str, str) output file name, file name in plex library
    """
    logging.info('Processing file {}'.format(input_file))
    f = pathlib.Path(input_file)

    input_filename = os.path.basename(input_file)
    # out_filename = input_filename.split('.')[0] + '.mkv'
    out_filename = os.path.splitext(input_filename)[0] + '.mkv'

    # print(filename)
    logging.info("Input file: {}".format(input_file))

    filename_split = f.name.split(' - ')

    # extract season from file name if file is in S01E01 format
    matched_season = re.search('S(\d*)E(\d*)', filename_split[1])

    # if not in S01E01 format, check if file is in yyyy-mm-dd format
    if not matched_season:
        matched_season = re.search('(\d*)-(\d*)-(\d*)', filename_split[1])

    folder = ['/home', 'plex'] # TODO setup library path via config
    folder.append(filename_split[0])
    folder.append('Season {}'.format(matched_season[1]))
    folder.append(f.name)

    moved_filename = os.path.join(*folder)
    logging.info("Moved file location: {}".format(moved_filename))
    out_filename = os.path.splitext(moved_filename)[0] + '.mkv'

    return out_filename, moved_filename


@app.task
def comcut(input_file):
    """
    Passes input_file name from Plex to comcut.
    :param input_file:
    :return:
    """
    out_filename, moved_filename = translate_filenames(input_file)
    cmd = [config['COMCUT_BINARY_PATH'], '--ffmpeg=/bin/ffmpeg', moved_filename]
    res = run(cmd)


def run(cmd, env=None):
    """Utility to execute command on local OS."""
    try:
        logging.info(' '.join(cmd))
        res = subprocess.check_output(cmd, stderr=subprocess.STDOUT, env=env)
        logging.debug(res)
        return res
    except subprocess.CalledProcessError as e:
        logging.warn(e.output)
        logging.warn(e.cmd)


def schedule(duration):
    """
    Used to limit time of day tasks can execute. Currenty set to run tasks between midnight and 8am daily.
    """
    c = inspect()
    tasks = c.scheduled()[config['CELERY_WORKER_NAME']]

    scheduled_task_duration = sum(map(lambda v: v['request']['kwargs']['vt_duration'], tasks))

    now = pendulum.now()
    window_start = now.replace(hour=config['SCHEDULE_START'], minute=0, second=0)
    window_end = now.replace(hour=config['SCHEDULE_END'], minute=0, second=0)

    # Move to next window if now is later than today's window end.
    if now > window_end:
        window_start += timedelta(days=1)
        window_end += timedelta(days=1)

    # how much of today's processing window is remaining?
    while True:
        window_size = (window_end - window_start).seconds
        remaining_window = scheduled_task_duration - window_size

        if scheduled_task_duration + duration <= window_size:
            return window_start + timedelta(seconds=(scheduled_task_duration))
        else:
            window_start += timedelta(days=1)
            window_end += timedelta(days=1)
            scheduled_task_duration -= window_size


@app.task
def comcut_and_transcode(input_file, **kwargs):
    """
    Passes input_file name from Plex to comcut then to ffmpeg.
    :param input_file:
    :return:
    """
    out_filename, moved_filename = translate_filenames(input_file)

    # cut commercials
    cmd = [config['COMCUT_BINARY_PATH'], moved_filename]
    res = run(cmd)

    # transcode to h265
    # cmd = [config['FFMPEG_BINARY_PATH'], '-i', moved_filename, '-c:v', 'libx265', '-crf', '24', '-c:a', 'copy', out_filename]
    cmd = [
        config['FFMPEG_BINARY_PATH'], 
        '-vsync', '0', 
        '-hwaccel', 'auto', 
        '-i', moved_filename, 
        '-c:v', 'hevc_nvenc', 
        '-rc:v', 'vbr_hq', 
        '-qmin:v', '22',
        '-qmax:v', '30', 
        '-rc-lookahead', '8', 
        '-weighted_pred', '1',
        out_filename]

    res = run(cmd, os.environ)

    # delete original file
    if config['DELETE_SOURCE_AFTER_TRANSCODE']:
        os.remove(moved_filename)


def video_metadata(filename):
    clip = me.VideoFileClip(filename)
    return clip.size, clip.duration


def is_regex(filename):
    return "*" in filename


def search(file_pattern):
    """Absolute path/s for given file pattern.
    
    Args:
        str: file pattern. See pathlib.Path.glob

    Returns:
        iterator: matched files
    """
    return map(str, pathlib.Path(os.getcwd()).glob(file_pattern))


def add_to_queue(filename, args):
    """Adds a single file to processing queue."""

    if args.action == 'transcode':
        pass # TODO
    elif args.action == 'comcut':
        if args.now:
            comcut.apply_async((filename,))
        else:
            comcut.apply_async((filename,), eta=schedule(5*60))
    elif args.action == 'comcut_and_transcode':
        frame_size, duration = video_metadata(filename)

        if args.now:
            comcut_and_transcode.apply_async(
                (filename,), 
                {'vt_frame_size': frame_size, 'vt_duration': duration}, 
                headers={'vt_frame_size': frame_size, 'vt_duration': duration})
        else:
            comcut_and_transcode.apply_async(
                (filename,), 
                {'vt_frame_size': frame_size, 'vt_duration': duration}, 
                eta=schedule(duration),
                headers={'vt_frame_size': frame_size, 'vt_duration': duration})


def main():
    args = parser.parse_args()

    for f in args.filename:
        # convert file name to absolute path
        filename = str(pathlib.Path(f).absolute())
        add_to_queue(filename, args)


if __name__ == '__main__':
    main()


