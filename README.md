What
====

An arduino collects information from sensors and other inputs, and writes all of that to the serial port.
zmq-publisher reads the serial port and publishes it on a zmq PUB socket. Other apps can subscribe to this
socket and do something with this info.

![bus](https://raw.githubusercontent.com/skopjehacklab/kika-info-bus/master/kika_info_bus.png)

For example, http-publisher will server the same data on a http request. It uses gevent (uwsgi or pywsgi) to
support long-poll connections, so it responds as soon as the data arrives from the zmq SUB socket.

The zmq publisher just pushes the data as it arrives from the arduino. For now, that looks like this:

    284C606340081,16.94,78758129,78761228
    282576B0300C7,17.19,78759154,78761229
    28B535930013,18.37,78760179,78761269
    285BEF57300C7,16.94,78761204,78761309
    status: CLOSED

which is the temperature readouts from 4 1-wire sensors, and lastly the state of the OPEN/CLOSE hacklab switch.
Exactly the same data is pushed by the http server too.


Install
=======

    sudo apt-get install libzmq3-dev python-dev
    PYTHONUSERBASE=$PWD/py-env pip install --user -r requirements.txt


Systemd Service
===============

To run in production you can use a recent enough Debian, Ubuntu or Arch. You can create an unpriviledged user for the
service (or even use the `DynamicUser=` systemd option on recent enough versions).

On debian stretch (9.0) install `nginx`, `uwsgi-core`, uwsgi-plugin-python` and `uwsgi-plugin-gevent-python`. uwsgi can
use systemd socket activation, so it's best to let systemd manage the socket - thus it can give the socket coresponding
permissions without having to run uwsgi itself with elevated privileges. The service is added to the dialout
SupplementaryGroup so that it can open the serial device.

`/etc/systemd/system/kika-info-bus.service`:
```
[Unit]
Description=kika-info-bus uwsgi services
After=network.target

[Service]
Type=notify
User=kikadevices
SupplementaryGroups=dialout
ExecStart=/usr/bin/uwsgi --ini /etc/uwsgi/kika-info-bus.ini --die-on-term
ExecReload=/bin/kill -HUP $MAINPID
ExecStop=/bin/kill -INT $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
Also=kika-info-bus.socket
```

`/etc/systemd/system/kika-info-bus.socket`:
```
[Unit]
Description=kika-info-bus socket

[Socket]
ListenStream=/run/kika-info-bus.sock
SocketMode=0660
SocketGroup=www-data

[Install]
WantedBy=sockets.target
```

In the end enable and start the service `systemctl enable --now kika-info-bus`


PS
==

We could've used MQTT instead of ZeroMQ maybe? Seems to be gaining popularity in the embedded and internet of things
world lately. Food for thought.
