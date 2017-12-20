# -*- encoding: utf-8 -*-
import re

def get_status(msg):
    match = re.search(r'\b(OPEN|CLOSED)\b', msg)
    if match is None:
        return None
    else:
        return match.group(1)

def get_temperature(msg):
    """Parses the arduino output and returns a data structure with sensorid to name mapings.
    """
    #sensorid to name mapping
    sensors = {
      "284C6063040000": { "name": "lounge_area" },
      "282576B0030000": { "name": "outside" },
      "28B50359030000": { "name": "hardware_room" },
      "285BEF57030000": { "name": "random_room" },
    }

    readouts = {}
    for line in msg.splitlines():
        try:
            sensor_addr,curr_temp,readout_millis = line.split(",")
        except ValueError:
            # ignore lines that are not sensors
            continue
        try:
            readouts[sensor_addr] = sensors[sensor_addr].copy()
            readouts[sensor_addr]['value'] = curr_temp
            readouts[sensor_addr]['readout_millis'] = readout_millis
        except KeyError:
            print "Unknown sensor found %s" % sensor_addr
            continue
    return readouts
