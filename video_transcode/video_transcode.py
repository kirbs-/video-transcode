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


# Load config.yaml
if os.environ.get('VIDEO_TRANSCODE_CONFIG'):
    CONFIG_FILE = os.environ.get('VIDEO_TRANSCODE_CONFIG')
else:
    CONFIG_FILE = pkg_resources.resource_filename('video_transcode','config/config.yaml')

with open(CONFIG_FILE) as f:
    config = yaml.full_load(f.read())
    os.environ['FFMPEG_BINARY'] = config['FFMPEG_BINARY_PATH']
    os.environ['LD_LIBRARY_PATH'] = '/usr/local/cuda/lib64'


# import moviepy after setting FFMPEG_BINARY
import moviepy.editor as me


parser = argparse.ArgumentParser()

parser.add_argument('filename')
parser.add_argument("-a", "--action",
                    help="ENVIRONMENT should be 'nonprod', 'dev' or 'sqa' and correspond to the AWS account to which you want to deploy.",
                    default=config['DEFAULT_ACTION'])
parser.add_argument("-n", "--now",
                    action='store_true',
                    help="Run action now; don't schedule.")



#FORMAT = '%(asctime)-15s %(levelname)-12s %(message)s'
#log_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger(__name__)
#handler = logging.FileHandler('log-{}.log'.format(log_timestamp))
#handler.setLevel(logging.INFO)
#handler.setFormatter(logging.Formatter(FORMAT))
#logger.addHandler(handler)
# CELERY_BROKER = 'redis://localhost:6379/0'

app = Celery(config['CELERY_QUEUE'], broker=config['CELERY_BROKER'], backend=config['CELERY_RESULT_BACKEND'])
# app.autodiscover_tasks(['video_transcode.video_transcode'])
app.conf.update(
    broker_transport_options = {'visibility_timeout': 604800}	
)


def translate_filenames(input_file):
    logging.info('Processing file {}'.format(input_file))
    f = pathlib.Path(input_file)

    input_filename = os.path.basename(input_file)
    # out_filename = input_filename.split('.')[0] + '.mkv'
    out_filename = os.path.splitext(input_filename)[0] + '.mkv'

    # print(filename)
    logging.info("Input file: {}".format(input_file))

    filename_split = f.name.split(' - ')

    # extract season
    matched_season = re.search('S(\d*)E(\d*)', filename_split[1])

    if not matched_season:
        matched_season = re.search('(\d*)-(\d*)-(\d*)', filename_split[1])

    folder = ['/home', 'plex']
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

        # try:
        #     return json.loads(res)
        # except:
        return res
    except subprocess.CalledProcessError as e:
        logging.info(e.output)
        logging.info(e.cmd)


# def schedule():
#     """
#     Used to limit time of day tasks can execute. Currenty set to run tasks between midnight and 8am daily.
#     """

#     c = inspect()
#     task_cnt = len(c.scheduled()[config['CELERY_WORKER_NAME']])

#     tomorrow = pendulum.tomorrow()
#     # tomorrow_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=int(task_cnt/24))
#     # tomorrow_8am = now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=int(task_cnt/24))
#     minute_offset = task_cnt % 24 * 20
#     scheduled_start = tomorrow + timedelta(minutes=minute_offset) + timedelta(seconds=10)
#     # print(str(scheduled_start))
#     return scheduled_start

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
        
#         print(f'Window size {window_size}')
#         print(f'Remaining window {remaining_window}')

        if scheduled_task_duration + duration <= window_size:
            return window_start + timedelta(seconds=(scheduled_task_duration))
        else:
            window_start += timedelta(days=1)
            window_end += timedelta(days=1)
            scheduled_task_duration -= window_size


# def eta(task_cnt, scheduled_start, tomorrow_midnight, tomorrow_8am):
#     """Keeps track of the number of comcut or transcode tasks in queue and schedules next task accordingly."""

#     if scheduled_start < tomorrow_8am:
#         return scheduled_start

#     if task_cnt > 24:
#         tomorrow_midnight += timedelta(days=1)
#         tomorrow_8am += timedelta(days=1)
#         task_cnt -= 24

#     minute_offset = task_cnt * 20
#     scheduled_start = tomorrow_midnight + timedelta(minutes=minute_offset) + timedelta(seconds=10)

#     return eta(task_cnt, scheduled_start, tomorrow_midnight, tomorrow_8am)

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


def main():
    args = parser.parse_args()

    if args.action == 'transcode':
        pass
    elif args.action == 'comcut':
        if args.now:
            comcut.apply_async((args.filename,))
        else:
            comcut.apply_async((args.filename,), eta=schedule(5*60))
    elif args.action == 'comcut_and_transcode':
        frame_size, duration = video_metadata(args.filename)

        if args.now:
            comcut_and_transcode.apply_async(
                (args.filename,), 
                {'vt_frame_size': frame_size, 'vt_duration': duration}, 
                headers={'vt_frame_size': frame_size, 'vt_duration': duration})
        else:
            comcut_and_transcode.apply_async(
                (args.filename,), 
                {'vt_frame_size': frame_size, 'vt_duration': duration}, 
                eta=schedule(duration),
                headers={'vt_frame_size': frame_size, 'vt_duration': duration})


if __name__ == '__main__':
    main()


