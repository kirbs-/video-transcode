# rpi2mqtt
Simplify reading Raspberry PI GPIO sensors and publish results to MQTT. 
 
# Installation
1. `git clone https://github.com/kirbs-/rpi2mqtt`
2. `sudo make`
3. `sudo make install`
4. update config.yaml
5. `sudo systemctl enable rpi2mqtt`
6. `sudo systemctl start rpi2mqtt`

# Supported Sensors
- Temperature
    - DHT22/DHT11
    - DS18B20
- Binary
    - Generic reed switches
    

# Setup MQTT
1. Open config.yaml.
2. Edit MQTT broker details
```yaml
# config.yaml
mqtt:
  host: example.com
  port: 8883
  ca_cert: '/path/to/example.com.crt'
  username: mqtt_user
  password: secure_password
  retries: 3
```
3\. add sensors to config.yaml
```yaml
# config.yaml
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

