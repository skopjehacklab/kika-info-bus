import serial
import zmq
from threading import Thread

DEV = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A600617K-if00-port0"
PUBSUB_ADDR = "tcp://*:5556"
REQREP_ADDR = "tcp://*:5557"

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
    socket.bind(PUBSUB_ADDR)

    #  Wait for message from arduino
    for message in read_until_delimiter(ser):
        socket.send(message)


def writer(ctx, ser):
    socket = ctx.socket(zmq.REP)
    socket.bind(REQREP_ADDR)

    while True:
        #  Wait for next request from 0mq client
        message = socket.recv()
        ser.write(message)
        socket.send('ok')


def main():
    ctx = zmq.Context()
    ser = serial.Serial(DEV, timeout=10)

    r = Thread(target=reader, args=[ctx, ser])
    w = Thread(target=writer, args=[ctx, ser])

    r.start()
    w.start()
    w.join()
    r.join()


if __name__ == '__main__':
    main()
