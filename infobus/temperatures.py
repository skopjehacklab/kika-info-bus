from __future__ import print_function

import datetime


def influx_update_temperatures(client, userdata, msg):
    now = datetime.datetime.utcnow()
    value = float(msg.payload)
    influx = userdata['influx']

    data = [{
        "measurement": "temperatures",
        "time": now.strftime('%Y-%m-%dT%H:%M:%SZ%z'),
        "tags": userdata['tags'],
        "fields": { "lounge_area": value }
    }]

    print(data)
    influx.write_points(data)
