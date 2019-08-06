# rpi2mqtt
Simplify reading GPIO sensors and publish to MQTT. Support systemd.
 
# Installation
`pip install rpi2mqtt`

# Setup
1. Copy config.yaml.
2. Add MQTT broker details
```yaml
mqtt:
  host: example.com
  port: 8883
  ca_cert: '/path/to/example.com.crt'
  username: mqtt_user
  password: secure_password
  retries: 3

sensors:
  - type: dht22
    name: laundry_room_climate
    pin: 16
    topic: 'homeassistant/sensor/laundry_room_climate/state'
  - type: reed
    name: laundry_room_door
    pin: 24
    normally_open: true
    topic: 'homeassistant/sensor/laundry_room_climate/state'
```
3. Start rpi2mqtt
`systemctl start rpi2mqtt`

