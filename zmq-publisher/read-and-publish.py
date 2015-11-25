#!/usr/bin/python2

import serial
import zmq
import os, ConfigParser

config = ConfigParser.RawConfigParser()


def read_until_delimiter(ser, delimiter='\r\n\r\n'):
    buffer = ''
    while True:
        char = ser.read(1) # watch out for timeouts???
        buffer += char
        messages = buffer.split(delimiter)
        if len(messages) > 1:
            for msg in messages[:-1]:
                yield msg + delimiter
            buffer = messages[-1]


def reader(ctx, ser):
    socket = ctx.socket(zmq.PUB)
    socket.bind(config.get('publisher', 'pub_addr'))

    #  Wait for message from arduino
    for message in read_until_delimiter(ser):
        socket.send(message)


def main():
    config.read(os.environ['CONFIG_FILE'])
    ctx = zmq.Context()
    ser = serial.Serial(config.get('publisher', 'serial_device'), timeout=10)
    ser.flushInput() #  reset_input_buffer() in pyserial 3.0
    reader(ctx, ser)

if __name__ == '__main__':
    main()
