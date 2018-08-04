import paho.mqtt.publish as mqtt
from config import config


def publish(topic, payload):
    mqtt.single(topic, payload, hostname=config.mqtt.host, port=config.mqtt.port,
                auth={'username': config.mqtt.username, 'password': config.mqtt.password},
                tls={'ca_certs': config.mqtt.ca_cert})
