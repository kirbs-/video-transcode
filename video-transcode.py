#!/home/kirby/.pyenv/versions/3.7.2/envs/video-transcode/bin/python
from celery import Celery
import subprocess
import sys
import json
import os
import logging
from celery.task.control import inspect
from datetime import datetime, timedelta
import pendulum
import pathlib
import shlex
import re


#FORMAT = '%(asctime)-15s %(levelname)-12s %(message)s'
#log_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger(__name__)
#handler = logging.FileHandler('log-{}.log'.format(log_timestamp))
#handler.setLevel(logging.INFO)
#handler.setFormatter(logging.Formatter(FORMAT))
#logger.addHandler(handler)
CELERY_BROKER = 'redis://localhost:6379/0'

app = Celery('video-transcode', broker=CELERY_BROKER)

app.conf.update(
    broker_transport_options = {'visibility_timeout': 604800}	
)

@app.task
def transcode(input_file):
    
    # input_file = sys.argv[0]
    logging.info('Processing file {}'.format(input_file))
    f = pathlib.Path(input_file)
    # logging.info('File check: {}'.format(f.is_file()))
    
    input_filedir = os.path.dirname(os.path.abspath(input_file))
    input_filename = os.path.basename(input_file)
    out_filename = input_filename.split('.')[0] + '.mkv'

    # print(filename)
    logging.info("Input file: {}".format(input_file))
    #sys.path.append('/usr/bin')
    #sys.path.append('/usr/local/bin')
    #logging.info(sys.path)
    #logging.info(subprocess.check_output(['which','comcut']))

    #cmd = ['/usr/local/bin/comcut']
    #os.chdir('/usr/local/bin')
    
    filename_split = f.name.split(' - ')
    
    # extract season
    matched_season = re.search('S(\d*)E(\d*)', filename_split[1])
    folder = ['/home','plex']
    folder.append(filename_split[0])
    folder.append('Season {}'.format(matched_season[1]))
    folder.append(f.name)

    moved_filename = os.path.join(*folder)
    logging.info("Moved file location: {}".format(moved_filename))    

    cmd = ['/usr/local/bin/comcut', moved_filename]
    #proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #res = proc.communicate('')
    #res = subprocess.check_output(cmd, stdin=ubprocess.STDOUT)
    res = run(cmd)
    #cmd = '/usr/local/bin/comcut '
    #cmd += shlex.quote(str(f))
    # logging.info(cmd)
    #res = subprocess.run(cmd, shell=True)

    #    logging.info(res)
    # cmd = ['ffmpeg', '-i', input_filename, '-c:v', 'libx265', '-c:a', 'copy', out_filename]
    # subprocess.check_output(cmd, stderr=subprocess.STDOUT)


def run(cmd):
    try:
        logging.info(' '.join(cmd))
        res = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        # logging.debug(res)
        try:
            return json.loads(res)
        except:
            return res
    except subprocess.CalledProcessError as e:
        # logging.debug(e.output)
        logging.info(e.output)
        logging.info(e.cmd)


def schedule():
    c = inspect()
    now = pendulum.now()
    tomorrow_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    tomorrow_8am = now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
    task_cnt = len(c.scheduled()['w1@brains'])
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
    logging.info("Received file from plex: {}".format(sys.argv[1]))
    #transcode.apply_async((sys.argv[1],))
    transcode.apply_async((sys.argv[1],), eta=schedule())
    sys.exit()
    #transcode(sys.argv[1])
