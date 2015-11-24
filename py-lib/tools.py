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
