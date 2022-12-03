import datetime


def influx_update_lan_devices(client, userdata, msg):
    now = datetime.datetime.utcnow()
    value = int(msg.payload)
    influx = userdata['influx']

    data = [{
       "measurement": "landevices",
       "time": now.strftime('%Y-%m-%dT%H:%M:%SZ%z'),
       "tags": { "location": "hacklab" },
       "fields": { "value": value }
    }]

    print(data)
    influx.write_points(data)
