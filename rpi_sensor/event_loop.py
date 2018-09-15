# import asyncio
from rpi_sensor.config import config
import RPi.GPIO as GPIO
from rpi_sensor.binary import *
import time
import rpi_sensor.mqtt as mqtt


for sensor in config.sensors:
    if sensor.type == 'reed':
        s = ReedSwitch(sensor.pin, sensor.topic, sensor.name, sensor.normally_closed)

    if s:
        GPIO.add_event_detect(sensor.pin, GPIO.RISING, callback=s.callback, bouncetime=500)

while True:
    mqtt.publish('homeassistant/binary_sensor/garage_door/config', '{"name": "Garage", "device_clase": "garage_door"}')
    time.sleep(1)
