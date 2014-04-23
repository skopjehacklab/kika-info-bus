#!/usr/bin/python2

import serial
import zmq
from threading import Thread
import os, ConfigParser

config = ConfigParser.RawConfigParser()
config.read(os.environ['CONFIG_FILE'])


def read_until_delimiter(ser, delimiter='\r\n\r\n'):
    buffer = ''
    while True:
        char = ser.read(1) # watch out for timeouts???
        buffer += char
        messages = buffer.split(delimiter)
        if len(messages) > 1:
            for msg in messages[:-1]:
                yield msg
            buffer = messages[-1]


def reader(ctx, ser):
    socket = ctx.socket(zmq.PUB)
    socket.bind(config.get('publisher', 'pub_addr'))

    #  Wait for message from arduino
    for message in read_until_delimiter(ser):
        socket.send(message)


def writer(ctx, ser):
    socket = ctx.socket(zmq.REP)
    socket.bind(config.get('publisher', 'rep_addr'))

    while True:
        #  Wait for next request from 0mq client
        message = socket.recv()
        ser.write(message)
        socket.send('ok')


def main():
    ctx = zmq.Context()
    ser = serial.Serial(config.get('publisher', 'serial_device'), timeout=10)

    r = Thread(target=reader, args=[ctx, ser])
    w = Thread(target=writer, args=[ctx, ser])

    r.start()
    w.start()
    w.join()
    r.join()


if __name__ == '__main__':
    main()
