# coding=utf-8
import Adafruit_DHT as dht
import json
import rpi2mqtt.mqtt as mqtt


class DHT(object):

    def __init__(self, pin, topic, name, device_class, dht_type):
        self.type = dht_type
        self.pin = pin
        self.topic = topic
        self.name = name
        self.device_class = device_class
        self.setup()

    def read(self, scale='F'):
        self.humidity, self.temperature = dht.read(22, self.pin)

        if scale == 'F':
            return json.dumps({'humidity': self.humidity, 'temperature': self.temperature_F})
        else:
            return json.dumps({'humidity': self.humidity, 'temperature': self.temperature})

    @property
    def temperature_F(self):
        try:
            return self.temperature_C * 1.8 + 32.0
        except:
            return -1.0

    @property
    def temperature_C(self):
        return self.temperature

    def setup(self):
        # config = json.dumps({'name': self.name, 'device_class': self.device_class})

        device_config = {'name': "Laundry Room Climate",
                         'identifiers': self.name,
                         'sw_version': 'rpi2mqtt',
                         'model': "DHT 22",
                         'manufacturer': 'Generic'}

        config = json.dumps({'name': self.name + '_temperature',
                             'device_class': 'temperature',
                             'unit_of_measurement': '°F',
                             'value_template': "{{ value_json.temperature }}",
                             'unique_id': self.name + '_temperature_rpi2mqtt',
                             'state_topic': self.topic,
                             "json_attributes_topic": self.topic,
                             'device': device_config})

        mqtt.publish('homeassistant/sensor/{}_{}/config'.format(self.name, 'temp'), config)

        config = json.dumps({'name': self.name + '_humidity',
                             'device_class': 'humidity',
                             'json_attributes_topic': self.topic,
                             'unit_of_measurement': '%',
                             'value_template': "{{ value_json.humidity }}",
                             'unique_id': self.name + '_humidity_rpi2mqtt',
                             'state_topic': self.topic,
                             'device': device_config})

        mqtt.publish('homeassistant/sensor/{}_{}/config'.format(self.name, 'humidity'), config)

    def state(self):
        return self.read()

    def payload(self):
        return json.dumps({'state': self.state()})
        # return self.state()

    def callback(self):
        mqtt.publish(self.topic, self.payload())