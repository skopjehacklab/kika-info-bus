# Kika Info Bus 2.0

Based on MQTT (old stuff, based on 0mq is in `legacy/`).

## publishers
* temp sensors
* open/closed button(s)
* PIR sensors
* bell door?
* openwrt num associations
* …

![mqtt](https://raw.githubusercontent.com/skopjehacklab/kika-info-bus/master/mqtt.png "MQTT")

## subscribers
* store to influxdb
* send twitter message
* send irc message
* open door
* LEDs in the hacklab
* LED strips in the hacklab
* LCD in the hacklab
* AC (turn off)
* …

## Python service

Listens on events from MQTT topics and sends it outside of the hacklab, to InfluxDB, Twitter and similar.
The systemd `.service` file assumes it's installed in `/srv/kika-info-bus`.
Configure paths and connection settings in it and put it in `/etc/systemd/system/`.

To install dependencies:
```
cd /srv/kika-info-bus
export PYTHONUSERBASE=$PWD/py-env
pip3 install --user -r requirements.txt
```

