from celery import Celery
from celery.task.control import	inspect

CELERY_BROKER = 'redis://localhost:6379/0'

app = Celery('video-transcode', broker=CELERY_BROKER)

tasks =	inspect().scheduled()['w1@brains']

#print(tasks[0]['request']['args'])

for task in tasks:
    print(task['request']['args'], task['eta'])

print("{} tasks in queue.".format(len(tasks)))
