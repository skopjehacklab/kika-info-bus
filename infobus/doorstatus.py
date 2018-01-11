from __future__ import print_function

import datetime

def get_last_status(influx):
    r = influx.query("SELECT doorstatus FROM doorstatus WHERE location='hacklab' ORDER BY time DESC LIMIT 1")
    return list(r['doorstatus'])[0]['doorstatus']


def bootup(client, userdata, msg):
    influx = userdata['influx']
    current_status = get_last_status(influx)
    client.publish('haklab/status', current_status)

def influx_toggle_doorstatus(client, userdata, msg):
    now = datetime.datetime.utcnow()
    if msg.payload != b'ON':
        return # ignore

    influx = userdata['influx']
    last_status = get_last_status(influx)

    current_status = 'CLOSED' if last_status == 'OPEN' else 'OPEN'

    data = [{
        "measurement": "doorstatus",
        "time": now.strftime('%Y-%m-%dT%H:%M:%SZ%z'),
        "tags": {
            "location": "hacklab"
        },
        "fields": { "doorstatus": current_status }
    }]

    print(data)
    influx.write_points(data)
    client.publish('haklab/status', current_status)
