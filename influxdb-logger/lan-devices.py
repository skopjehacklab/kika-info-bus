#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-
from influxdb import InfluxDBClient
import os, datetime, ConfigParser
import subprocess

config = ConfigParser.RawConfigParser()
config.read(os.environ['CONFIG_FILE'])

CMD = ['ip', '-4', 'neigh', 'list', 'dev', 'enp1s1', 'nud', 'reachable']
BLACKLIST = [
 '00:0c:76:5d:1c:9c',
 '00:20:4a:e0:1e:a3',
 'b8:27:eb:1b:dd:cf',
 '50:90:00:48:24:01',
 '64:70:02:b0:38:de',
 '00:20:4a:e0:1e:a3',
 'b8:27:eb:64:0a:63',
 'b8:27:eb:18:80:7d'
]

def main():
    result = subprocess.check_output(CMD)

    results = [line.split() for line in result.splitlines()]
    alldevices = [row for row in results if row[0].startswith('192.168.88.')]
    devices = [row for row in alldevices if row[2] not in BLACKLIST]

    dsn = config.get('influxdb', 'database')
    client = InfluxDBClient.from_DSN(dsn, timeout=5)

    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ%z')
    data = [{
            "measurement": "landevices",
            "time": now,
            "tags": { "location": "hacklab" },
            "fields": { "value": len(devices), "total": len(alldevices) }
        }]

    client.write_points(data)

if __name__ == '__main__':
    main()
