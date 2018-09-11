import RPi.GPIO as GPIO
import mqtt
import json


class Sensor(object):

    def __init__(self, pin, topic):
        self.pin = pin
        self.topic = topic


class ReedSwitch(object):
    """
    Extends simple binary sensor by adding configuration for normally open or normally closed reed switches.
    """

    def __init__(self, pin, topic, normally_open):
        self.pin = pin
        self.topic = topic
        self.normally_open = normally_open
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
        return GPIO.input(self.pin)

    def payload(self, args):
        return json.dumps({'state': self.state()})

    def callback(self):
        mqtt.publish(self.topic, self.payload())
