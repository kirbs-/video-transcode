import Adafruit_DHT as dht
import json
import rpi_sensor.mqtt as mqtt


class DHT(object):

    def __init__(self, pin, topic, name, device_class, dht_type):
        self.type = dht_type
        self.pin = pin
        self.topic = topic
        self.name = name
        self.device_class = device_class
        self.setup()

    def read(self, scale='F'):
        self.humidity, self.temperature = dht.read(self.dht_type, self.pin) #dht.read(22, 18)

        if scale == 'F':
            return json.dumps({'humidity': self.humidity, 'temperature': self.temperature_F})
        else:
            return json.dumps({'humidity': self.humidity, 'temperature': self.temperature})

    @property
    def temperature_F(self):
        return self.temperature_C * 1.8 + 32.0

    @property
    def temperature_C(self):
        return self.temperature

    def setup(self):
        mqtt.publish('homeassistant/binary_sensor/{name}/config',
                     '{"name": "{name}", "device_class": "garage_door"}'.format({'name': self.name, self.device_class}))

    def state(self):
        return self.read()

    def payload(self):
        # return json.dumps({'state': self.state()})
        return self.state()

    def callback(self, pin):
        mqtt.publish(self.topic, self.payload())