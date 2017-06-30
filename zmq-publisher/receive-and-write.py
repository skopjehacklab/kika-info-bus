#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

import serial
import zmq
import os, ConfigParser

config = ConfigParser.RawConfigParser()

def main():
    config.read(os.environ['CONFIG_FILE'])
    ser = serial.Serial(config.get('publisher', 'serial_device'), timeout=10)

    ctx = zmq.Context()
    socket = ctx.socket(zmq.REP)
    socket.bind(config.get('publisher', 'rep_addr'))

    while True:
        #  Wait for next request from 0mq client
        message = socket.recv()
        ser.write(message)
        socket.send('ok')


if __name__ == '__main__':
    main()
