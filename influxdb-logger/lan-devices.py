#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

from influxdb import InfluxDBClient
import os, datetime, ConfigParser
import subprocess

config = ConfigParser.RawConfigParser()
config.read(os.environ['CONFIG_FILE'])

CMD = ['ip', '-4', 'neigh', 'list', 'dev', 'enp1s1', 'nud', 'reachable']
BLACKLIST = config.get('Lan Devices', 'exclude_list').splitlines()

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
