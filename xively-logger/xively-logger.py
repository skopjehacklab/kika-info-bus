#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-
import zmq
import requests
import json
import os, re, datetime, ConfigParser

from tools import get_temperature, get_status

config = ConfigParser.RawConfigParser()
config.read(os.environ['CONFIG_FILE'])


ctx = zmq.Context()

def main():
    socket = ctx.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, '')
    socket.connect(config.get('zmq', 'publisher_addr'))

    msg = socket.recv()
    current_status = get_status(msg)
    current_sensors = get_temperature(msg)

    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ%z')

    #post Current Status
    url="http://api.xively.com/v2/feeds/%s/datastreams/%s/datapoints" % (config.get('xively-status','feed_id'),'hacklab_status')
    headers = {'X-ApiKey':config.get('xively-status','api_key')}
    value = 1 if current_status == 'OPEN' else 0

    payload={'datapoints': [{'at': now, 'value': value}]}
    r = requests.post(url, data=json.dumps(payload), headers=headers)

    #post Current temperature values
    for sensor in current_sensors.itervalues():
        url="http://api.xively.com/v2/feeds/%s/datastreams/%s/datapoints" % (config.get('xively-temperature','feed_id'),sensor['name'])
        headers = {'X-ApiKey':config.get('xively-temperature','api_key')}
        value = sensor['value']

        payload={'datapoints': [{'at': now, 'value': value}]}
        r = requests.post(url, data=json.dumps(payload), headers=headers)

if __name__ == '__main__':
    main()
