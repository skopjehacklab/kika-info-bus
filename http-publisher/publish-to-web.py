# run with
# uwsgi --plugins python,gevent --gevent 1000 --http-socket :5001 --wsgi-file ...

from flask import Flask, Response
import zmq.green as zmq
import gevent
import gevent.event
import os, ConfigParser

config = ConfigParser.RawConfigParser()
config.read(os.environ['CONFIG_FILE'])

ctx = zmq.Context()

app = Flask(__name__)

@app.before_first_request
def run():
    app.latest_message = gevent.event.AsyncResult()
    def _process():
        socket = ctx.socket(zmq.SUB)
        socket.setsockopt(zmq.SUBSCRIBE, '')
        socket.connect(config.get('zmq', 'publisher_addr'))
        while True:
            msg = socket.recv()
            app.latest_message.set(msg)
            app.latest_message = gevent.event.AsyncResult()

    gevent.spawn(_process)


@app.route('/')
def index():
    msg = app.latest_message.get()
    return Response(msg, content_type='text/plain; charset=utf-8')

@app.route('/open')
def openclosed():
    status = 'OPEN' in app.latest_message.get()
    # don't wait forever, only do several iterations waiting for a change in status
    # since the client might have aborted the request
    for i in range(100):
        new_status = 'OPEN' in app.latest_message.get()
        if new_status != status:
            msg = 'OPEN\n' if new_status else 'CLOSED\n'
            return Response(msg, content_type='text/plain; charset=utf-8')
    return Response(status=204)

@app.route('/longpoll')
def longpoll():
    msg = app.latest_message.get()
    return Response(msg, content_type='text/plain; charset=utf-8')

if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    app.debug = True
    WSGIServer(('', 8088), app).serve_forever()
else:
    application = app
