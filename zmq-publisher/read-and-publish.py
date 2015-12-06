#!/usr/bin/python2

import serial
import zmq
import os, ConfigParser

config = ConfigParser.RawConfigParser()


def read_until_delimiter(input_stream, delimiter=b'\r\n\r\n'):
    buffer = bytearray()
    for data in input_stream:
        buffer += data
        messages = buffer.split(delimiter)
        if len(messages) > 1:
            for msg in messages[:-1]:
                yield msg + delimiter
            buffer = messages[-1]


def reader(ctx, serial_stream):
    socket = ctx.socket(zmq.PUB)
    socket.bind(config.get('publisher', 'pub_addr'))

    #  Wait for message from arduino
    for message in read_until_delimiter(serial_stream):
        socket.send(message)


def main():
    config.read(os.environ['CONFIG_FILE'])
    ctx = zmq.Context()
    ser = serial.Serial(config.get('publisher', 'serial_device'), timeout=10)
    ser.flushInput() #  reset_input_buffer() in pyserial 3.0
    reader(ctx, iter(lambda: ser.read(100), None))

if __name__ == '__main__':
    main()
