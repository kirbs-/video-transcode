#! /home/kirby/.pyenv/versions/3.7.2/envs/video-transcode/bin/
from celery import Celery
import subprocess
import sys
import json
import os
import logging

CELERY_BROKER = 'redis://localhost:6379/0'

app = Celery('transcode-tasks', broker=CELERY_BROKER)


@app.task
def transcode():
    input_file = sys.argv[0]
    input_filedir = os.path.dirname(os.path.abspath(input_file))
    input_filename = os.path.basename(input_file)
    out_filename = input_filename.split('.')[0] + '.mkv'

    # print(filename)

    cmd = ['comcut', input_file]
    run(cmd)

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


if __name__ == '__main__':
    transcode()