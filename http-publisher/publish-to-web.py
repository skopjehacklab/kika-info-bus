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
    app.last_known_status = None
    app.live_status = gevent.event.AsyncResult()
    def _process():
        socket = ctx.socket(zmq.SUB)
        socket.setsockopt(zmq.SUBSCRIBE, '')
        socket.connect(config.get('zmq', 'publisher_addr'))
        while True:
            msg = socket.recv()
            app.last_known_status = msg
            app.live_status.set(msg)
            app.live_status = gevent.event.AsyncResult()

    gevent.spawn(_process)


@app.route('/')
def index():
    msg = app.last_known_status
    if msg is None:
        return Response(status=204)
    return Response(msg, content_type='text/plain; charset=utf-8')

@app.route('/open')
def openclosed():
    status = 'OPEN' in app.live_status.get()
    new_status = status
    # don't wait forever, since the client might have aborted the request
    with gevent.Timeout(300, False):
        while new_status == status:
            new_status = 'OPEN' in app.live_status.get()
    if new_status != status:
        msg = 'OPEN\n' if new_status else 'CLOSED\n'
        return Response(msg, content_type='text/plain; charset=utf-8')
    else:
        return Response(status=204)

@app.route('/longpoll')
def longpoll():
    msg = app.live_status.get()
    return Response(msg, content_type='text/plain; charset=utf-8')

if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    app.debug = True
    WSGIServer(('', 8088), app).serve_forever()
else:
    application = app
