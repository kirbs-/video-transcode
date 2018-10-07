import paho.mqtt.publish as mqtt
from config import config


def publish(topic, payload, cnt=1):
    try:
        if cnt <= config.mqtt.retries:
            mqtt.single(topic, payload, hostname=config.mqtt.host, port=config.mqtt.port,
                        auth={'username': config.mqtt.username, 'password': config.mqtt.password},
                        tls={'ca_certs': config.mqtt.ca_cert})
    except:
        cnt += 1
        publish(topic, payload, cnt)
