#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

import zmq
from influxdb import InfluxDBClient
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

    dsn = config.get('influxdb', 'database')
    client = InfluxDBClient.from_DSN(dsn, timeout=5)

    msg = socket.recv()
    current_status = get_status(msg)
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ%z')

    r = client.query("SELECT doorstatus FROM doorstatus WHERE location='hacklab' ORDER BY time DESC LIMIT 1")
    last_status = list(r['doorstatus'])[0]['doorstatus']

    if current_status == last_status:
        return
    data = [
        {
            "measurement": "doorstatus",
            "time": now,
            "tags": {
                "location": "hacklab"
            },
            "fields": { "doorstatus": current_status }
        }
    ]
    client.write_points(data)


if __name__ == '__main__':
    main()

