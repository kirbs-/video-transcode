# import asyncio
from rpi2mqtt.config import config
import RPi.GPIO as GPIO
from rpi2mqtt.binary import *
from rpi2mqtt.temperature import *
import time
import rpi2mqtt.mqtt as mqtt


def main():
    sensor_list = []

    for sensor in config.sensors:
        s = DHT(sensor.pin, sensor.topic, sensor.name, 'sensor', sensor.type)
        # s.setup()
        sensor_list.append(s)

    while True:
        for sensor in sensor_list:
            sensor.callback()


if __name__ == '__main__':
    main()