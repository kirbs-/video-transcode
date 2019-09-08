from rpi2mqtt.binary import Sensor
import rpi2mqtt.mqtt as mqtt
import json
from datetime import datetime, timedelta


class Scanner(Sensor):

    def __init__(self, name, topic, beacon_uuid, away_timeout=10):
        super(Scanner, self).__init__(None, topic)
        self.name = name
        self.present = 'OFF'
        self.rssi = None
        self.beacon_uuid = beacon_uuid
        self.away_timeout = away_timeout
        self.last_seen = datetime.now()
        self.setup()

    def setup(self):
        """
        Setup Home Assistant MQTT discover for ibeacons.
        :return: None
        """
        device_config = {'name': "iBeacon",
                         'identifiers': self.name,
                         'sw_version': 'rpi2mqtt',
                         'model': "iBeacon",
                         'manufacturer': 'Generic'}

        config = json.dumps({'name': self.name + '_ibeacon',
                             'device_class': 'presence',
                             'value_template': "{{ value_json.presence }}",
                             'unique_id': self.name + '_ibeacon_rpi2mqtt',
                             'state_topic': self.topic,
                             "json_attributes_topic": self.topic,
                             'device': device_config})

        mqtt.publish('homeassistant/binary_sensor/{}_{}/config'.format(self.name, 'presence'), config)

    def process_ble_update(self, bt_addr, rssi, packet, additional_info):
        new_state = self.present
        if self.beacon_uuid == additional_info['uuid']:
            new_state = 'ON'
        self.rssi = rssi
        self.last_seen = datetime.now()

        if new_state != self.present:
            self.present = new_state
            self.callback()

    def state(self):
        if self.present == 'ON' and self.last_seen + timedelta(seconds=self.away_timeout) < datetime.now():
            self.present = 'OFF'

        return json.dumps({'presence': self.present, 'rssi': self.rssi})

    def payload(self):\
        return self.state()

    def callback(self):
        mqtt.publish(self.topic, self.payload())