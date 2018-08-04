import RPi.GPIO as GPIO
import mqtt


class Sensor(object):

    def __init__(self, pin):
        pass


class ReedSwitch(object):

    def __init__(self, pin, normally_open):
        self.pin = pin
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

    def payload(self):
        return {'state': self.state()}

    def callback(self, topic):
        mqtt.publish(topic, self.payload())