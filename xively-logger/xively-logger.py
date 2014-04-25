#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-
import zmq
import requests
import json
import os, re, datetime, ConfigParser


config = ConfigParser.RawConfigParser()
config.read(os.environ['CONFIG_FILE'])


ctx = zmq.Context()

def get_status(msg):
    match = re.search(r'\b(OPEN|CLOSED)\b', msg)
    return match.group(1)

def get_temperature(msg):
    #sensorid to name mapping
    sensors = {
            "28B535930013": {  
                                "name": "hardware_room", 
                                "value": "", "readout_time": "", "current_millis": "" 
                            },
            "284C606340081": { 
                                "name": "lounge_area", 
                                "value": "", "readout_time": "", "current_millis": "" 
                            },
            "285BEF57300C7": { 
                                "name": "random_room", 
                                "value": "", "readout_millis": "", "current_millis": "" 
                            },
            "282576B0300C7": { 
                                "name": "outside", 
                                "value": "", "readout_time": "", "current_millis": "" 
                            },
    }

    for line in msg.splitlines()[:-1]: 
        sensor_addr,curr_temp,readout_millis,current_millis = line.split(",")

        try:
            sensors[sensor_addr]['value'] = curr_temp
            sensors[sensor_addr]['readout_millis'] = readout_millis
            sensors[sensor_addr]['current_millis'] = current_millis
        except KeyError:
            print "Unknown sensor found %s" % sensor_addr
            continue

        if int(current_millis)-int(readout_millis)>300000:
            print "Haven't read new reading from %s for over 5 minutes." % datapoint_id
            continue

    return sensors

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
