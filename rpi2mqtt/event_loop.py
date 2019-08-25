# import asyncio
from rpi2mqtt.config import config
import RPi.GPIO as GPIO
from rpi2mqtt.binary import *
from rpi2mqtt.temperature import *
import time
import rpi2mqtt.mqtt as mqtt


# for sensor in config.sensors:
#     if sensor.type == 'reed':
#         s = ReedSwitch(sensor.pin, sensor.topic, sensor.name, sensor.normally_closed)
#
#     if s:
#         GPIO.add_event_detect(sensor.pin, GPIO.RISING, callback=s.callback, bouncetime=500)
#
# mqtt.publish('homeassistant/binary_sensor/garage_door/config', '{"name": "Garage", "device_class": "garage_door"}')
#
# while True:
#     #mqtt.publish('homeassistant/binary_sensor/garage_door/config', '{"name": "Garage", "device_class": "garage_door"}')
#     time.sleep(15)


def main():
    sensor_list = []

    for sensor in config.sensors:
        s = DHT(sensor.pin, sensor.topic, sensor.name, 'sensor', sensor.type)
        # s.setup()
        sensor_list.append(s)

    for i in range(10):
        for sensor in sensor_list:
            sensor.callback()


if __name__ == '__main__':
    main()