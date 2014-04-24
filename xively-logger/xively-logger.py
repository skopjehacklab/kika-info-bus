#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-
import zmq
import requests
import json
import os, re, datetime, ConfigParser


config = ConfigParser.RawConfigParser()
config.read(os.environ['CONFIG_FILE'])


ctx = zmq.Context()

def get_value(msg):
    match = re.search(r'\b(OPEN|CLOSED)\b', msg)
    return match.group(1)

def get_temperature(msg):
    return false

def main():
    socket = ctx.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, '')
    socket.connect(config.get('zmq', 'publisher_addr'))

    url="http://api.xively.com/v2/feeds/%s/datastreams/%s/datapoints" % (config.get('xively','feed_id'),"hacklab_status")
    headers = {'X-ApiKey':config.get('xively','api_key')}

    msg = socket.recv()
    current_value = get_value(msg)
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ%z')
        
    if current_value == 'OPEN':
        payload={'datapoints': [{'at': now, 'value': 1}]}
    if current_value == 'CLOSED':
        payload={'datapoints': [{'at': now, 'value': 0}]}

    r = requests.post(url, data=json.dumps(payload), headers=headers)

if __name__ == '__main__':
    main()
