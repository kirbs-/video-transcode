import RPi.GPIO as GPIO
import rpi_sensor.mqtt as mqtt
import json


class Sensor(object):

    def __init__(self, pin, topic):
        self.pin = pin
        self.topic = topic


class ReedSwitch(object):
    """
    Extends simple binary sensor by adding configuration for normally open or normally closed reed switches.
    """

    def __init__(self, pin, topic, name, normally_open):
        self.pin = pin
        self.topic = topic
        self.normally_open = normally_open
        self.name = name
        GPIO.setmode(GPIO.BCM)
        self.setup()

    def setup(self):
        """
        Setup GPIO pin to read input value.
        :return: None
        """
        if self.normally_open:
            mode = GPIO.PUD_UP
        else:
            mode = GPIO.PUD_DOWN

        GPIO.input(self.pin, GPIO.IN, pull_up_down=mode)

    def state(self):
        if GPIO.input(self.pin) == 1:
            return "OFF"
        else:
            return "ON"

    def payload(self):
        # return json.dumps({'state': self.state()})
        return self.state()

    def callback(self, pin):
        mqtt.publish(self.topic, self.payload())
