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
    CLOSED

which is the temperature readouts from 4 1-wire sensors, and lastly the state of the OPEN/CLOSE hacklab switch.
Exactly the same data is pushed by the http server too.


Install
=======

    sudo apt-get install libzmq3-dev python-dev
    PYTHONUSERBASE=$PWD/py-env pip install --user -r requirements.txt
