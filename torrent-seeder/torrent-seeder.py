#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-
import zmq
import os, re, ConfigParser

from tools import get_status

config = ConfigParser.RawConfigParser()
config.read(os.environ['CONFIG_FILE'])

ctx = zmq.Context()

def main():
    socket = ctx.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, '')
    socket.connect(config.get('zmq', 'publisher_addr'))

    msg = socket.recv()
    previous_value = get_status(msg)

    while True:
        msg = socket.recv()
        current_value = get_status(msg)
        if current_value != previous_value:
            if current_value == 'OPEN':
                os.system("/usr/bin/transmission-remote --torrent all --stop 2>&1 > /dev/null")
            if current_value == 'CLOSED':
                os.system("/usr/bin/transmission-remote --torrent all --start 2>&1 > /dev/null")
        previous_value = current_value


if __name__ == '__main__':
    main()
