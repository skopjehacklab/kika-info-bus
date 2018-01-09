from __future__ import print_function
import paho.mqtt.client
import influxdb
import sdnotify

from .landevices import influx_update_lan_devices
from .temperatures import influx_update_temperatures
from .doorstatus import influx_toggle_doorstatus

import os

def on_connect(client, userdata, flags, rc):
    client.message_callback_add('haklab/hodnik/button', influx_toggle_doorstatus)
    client.message_callback_add('haklab/wifi/landevices', influx_update_lan_devices)
    client.message_callback_add('haklab/+/temp', influx_update_temperatures)

    sn = sdnotify.SystemdNotifier()
    sn.notify("READY=1")

def main():
    # config
    MQTT = os.environ.get('MQTT_SERVER', '127.0.0.1')
    INFLUX = os.environ['INFLUX_SERVER']

    influx = influxdb.InfluxDBClient.from_dsn(INFLUX, timeout=5)
    userdata = dict()
    userdata['influx'] = influx
    userdata['tags'] = { "location": "hacklab" }

    mqtt = paho.mqtt.client.Client(client_id='1eecf04e-b3f2-4ada-8b89-0767a1338725',
            clean_session=False, userdata=userdata)
    mqtt.on_connect = on_connect

    mqtt.connect(MQTT)
    mqtt.loop_forever()

if __name__ == '__main__':
    main()
