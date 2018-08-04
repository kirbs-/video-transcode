# import asyncio
from config import config
import RPi.GPIO as GPIO
from rpi_sensor.binary import *


for sensor in config.sensors:
    if sensor.type == 'reed':
        s = ReedSwitch(sensor.pin, sensor.normally_closed)

    if s:
        GPIO.add_event_detect(sensor.pin, GPIO.RISING, callback=s.callback(sensor.topic))

while True:
    pass
