#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-
import zmq
from influxdb import InfluxDBClient
import json
import os, re, datetime, ConfigParser

from tools import get_temperature

config = ConfigParser.RawConfigParser()
config.read(os.environ['CONFIG_FILE'])


ctx = zmq.Context()

def get_status(msg):
    match = re.search(r'\b(OPEN|CLOSED)\b', msg)
    return match.group(1)

def main():
    socket = ctx.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, '')
    socket.connect(config.get('zmq', 'publisher_addr'))

    dsn = config.get('influxdb', 'database')
    client = InfluxDBClient.from_DSN(dsn, timeout=5)

    msg = socket.recv()
    current_status = get_status(msg)
    current_sensors = get_temperature(msg)

    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ%z')
    data = [
        {
            "measurement": "temperatures",
            "time": now,
            "tags": {
                "location": "hacklab"
            },
            "fields": { o['name']: float(o['value']) for o in current_sensors.values() }
        }
    ]

    client.write_points(data)

if __name__ == '__main__':
    main()
