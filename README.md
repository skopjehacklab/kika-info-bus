What
====

An arduino collects information from sensors and other inputs, and writes all of that to the serial port.
zmq-publisher reads the serial port and publishes it on a zmq PUB socket. Other apps can subscribe to this
socket and do something with this info.

For example, http-publisher will server the same data on a http request. It uses gevent (uwsgi or pywsgi) to
support long-poll connections, so it responds as soon as the data arrives from the zmq SUB socket.



Install
=======

    sudo apt-get install libzmq3-dev python-dev
    PYTHONUSERBASE=$PWD/py-env pip install --user -r requirements.txt
