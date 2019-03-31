#! /home/kirby/.pyenv/versions/3.7.2/envs/video-transcode/bin/
from celery import Celery
import subprocess
import sys
import json
import os
import logging
from celery.task.control import inspect
from datetime import datetime, timedelta
import pendulum


FORMAT = '%(asctime)-15s %(levelname)-12s %(message)s'
log_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('video-traanscode-{}.log'.format(log_timestamp))
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(handler)
CELERY_BROKER = 'redis://localhost:6379/0'

app = Celery('video-transcode', broker=CELERY_BROKER)

@app.task
def transcode(input_file):
    # input_file = sys.argv[0]
    logging.info('Processing file {}'.format(input_file))
    input_filedir = os.path.dirname(os.path.abspath(input_file))
    input_filename = os.path.basename(input_file)
    out_filename = input_filename.split('.')[0] + '.mkv'

    # print(filename)

    cmd = ['comcut', input_file]
    res = run(cmd)

    logging.info(res)
    # cmd = ['ffmpeg', '-i', input_filename, '-c:v', 'libx265', '-c:a', 'copy', out_filename]
    # subprocess.check_output(cmd, stderr=subprocess.STDOUT)


def run(cmd):
    try:
        logging.debug(' '.join(cmd))
        res = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        # logging.debug(res)
        try:
            return json.loads(res)
        except:
            return res
    except subprocess.CalledProcessError as e:
        # logging.debug(e.output)
        print(e.output)


def schedule():
    c = inspect()
    now = pendulum.now()
    tomorrow_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    tomorrow_8am = now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
    task_cnt = c.scheduled()
    minute_offset = task_cnt * 20
    scheduled_start = tomorrow_midnight + timedelta(minutes=minute_offset) + timedelta(seconds=10)

    return eta(task_cnt, scheduled_start, tomorrow_midnight, tomorrow_8am)


def eta(task_cnt, scheduled_start, tomorrow_midnight, tomorrow_8am):
    #     print(schedule < tomorrow_8am)
    #     print(schedule)
    if scheduled_start < tomorrow_8am:
        return scheduled_start

    if task_cnt > 24:
        tomorrow_midnight += timedelta(days=1)
        tomorrow_8am += timedelta(days=1)
        task_cnt -= 24

    minute_offset = task_cnt * 20
    scheduled_start = tomorrow_midnight + timedelta(minutes=minute_offset) + timedelta(seconds=10)
    #     print(task_cnt)
    #     print(tomorrow_midnight)
    #     print(schedule)
    #     print(tomorrow_8am)
    return eta(task_cnt, scheduled_start, tomorrow_midnight, tomorrow_8am)


if __name__ == '__main__':
    transcode.delay(sys.argv[0], eta=schedule())