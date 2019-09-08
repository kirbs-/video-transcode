# import asyncio
from rpi2mqtt.config import config
import RPi.GPIO as GPIO
from rpi2mqtt.binary import *
from rpi2mqtt.temperature import *
from rpi2mqtt.ibeacon import Scanner
import time
import rpi2mqtt.mqtt as mqtt
from beacontools import BeaconScanner, IBeaconFilter


def main():
    sensor_list = []

    for sensor in config.sensors:
        if sensor.type == 'dht22':
            s = DHT(sensor.pin, sensor.topic, sensor.name, 'sensor', sensor.type)
        elif sensor.type == 'ibeacon':
            s = Scanner(sensor.name, sensor.topic, sensor.uuid, sensor.away_timeout)

        sensor_list.append(s)

    scanner = BeaconScanner()
    scanner.start()

    try:
        while True:

            for sensor in sensor_list:
                sensor.callback()

            time.sleep(300)

    except:
        scanner.stop()


if __name__ == '__main__':
    main()