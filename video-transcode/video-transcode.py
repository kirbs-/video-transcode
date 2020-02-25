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
with open(pkg_resources.resource_filename('video-transcode','config/config.yaml')) as f:
    config = yaml.full_load(f.read())

parser = argparse.ArgumentParser()

parser.add_argument('filename')
parser.add_argument("-a", "--action",
                    help="ENVIRONMENT should be 'nonprod', 'dev' or 'sqa' and correspond to the AWS account to which you want to deploy.",
                    default=config['DEFAULT_ACTION'])


#FORMAT = '%(asctime)-15s %(levelname)-12s %(message)s'
#log_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger(__name__)
#handler = logging.FileHandler('log-{}.log'.format(log_timestamp))
#handler.setLevel(logging.INFO)
#handler.setFormatter(logging.Formatter(FORMAT))
#logger.addHandler(handler)
# CELERY_BROKER = 'redis://localhost:6379/0'

app = Celery(config['CELERY_QUEUE'], broker=config['CELERY_BROKER'])

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
    cmd = [config['COMCUT_BINARY_PATH'], moved_filename]
    res = run(cmd)


def run(cmd):
    """Utility to execute command on local OS."""
    try:
        logging.info(' '.join(cmd))
        res = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        logging.debug(res)

        # try:
        #     return json.loads(res)
        # except:
        return res
    except subprocess.CalledProcessError as e:
        logging.info(e.output)
        logging.info(e.cmd)


def schedule():
    """
    Used to limit time of day tasks can execute. Currenty set to run tasks between midnight and 8am daily.
    """

    c = inspect()
    now = pendulum.now()
    tomorrow_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    tomorrow_8am = now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
    task_cnt = len(c.scheduled()[config['CELERY_WORKER_NAME']])
    minute_offset = task_cnt * 20
    scheduled_start = tomorrow_midnight + timedelta(minutes=minute_offset) + timedelta(seconds=10)

    return eta(task_cnt, scheduled_start, tomorrow_midnight, tomorrow_8am)


def eta(task_cnt, scheduled_start, tomorrow_midnight, tomorrow_8am):
    """Keeps track of the number of comcut or transcode tasks in queue and schedules next task accordingly."""

    if scheduled_start < tomorrow_8am:
        return scheduled_start

    if task_cnt > 24:
        tomorrow_midnight += timedelta(days=1)
        tomorrow_8am += timedelta(days=1)
        task_cnt -= 24

    minute_offset = task_cnt * 20
    scheduled_start = tomorrow_midnight + timedelta(minutes=minute_offset) + timedelta(seconds=10)

    return eta(task_cnt, scheduled_start, tomorrow_midnight, tomorrow_8am)

@app.task
def comcut_and_transcode(input_file):
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
    cmd = [config['FFMPEG_BINARY_PATH'], '-i', moved_filename, '-c:v', 'libx265', '-c:a', 'copy', out_filename]
    res = run(cmd)

    # delete original file
    if config['DELETE_SOURCE_AFTER_TRANSCODE']:
        os.remove(moved_filename)


# if __name__ == '__main__':
#     if len(sys.argv) == 2:
#         comcut.apply_async((sys.argv[1],), eta=schedule())
#     else:
#         comcut_and_transcode.apply_async((sys.argv[1],))

#     sys.exit()

def main():
    args = parser.parse_args()

    if args.action == 'transcode':
        pass
    elif args.action == 'comcut':
        comcut.apply_async((args.filename,), eta=schedule())
    elif args.action == 'comcut_and_transcode':
        comcut_and_transcode.apply_async((args.filename,), eta=schedule())