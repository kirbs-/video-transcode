# import asyncio
from config import config
import RPi.GPIO as GPIO
from rpi_sensor.binary import *
import time


for sensor in config.sensors:
    if sensor.type == 'reed':
        s = ReedSwitch(sensor.pin, sensor.topic, sensor.normally_closed)

    if s:
        GPIO.add_event_detect(sensor.pin, GPIO.RISING, callback=s.callback)

while True:
    time.sleep(1)
