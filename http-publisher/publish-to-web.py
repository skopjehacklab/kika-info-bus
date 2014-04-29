# run with
# uwsgi --plugins python,gevent --gevent 1000 --http-socket :5001 --wsgi-file ...

from flask import Flask, Response
import zmq.green as zmq
import gevent
import gevent.queue
import os, ConfigParser

config = ConfigParser.RawConfigParser()
config.read(os.environ['CONFIG_FILE'])

ctx = zmq.Context()

app = Flask(__name__)

@app.before_first_request
def run():
    app.latest_message = None
    app.waiters_queue = gevent.queue.Queue()
    def _process():
        socket = ctx.socket(zmq.SUB)
        socket.setsockopt(zmq.SUBSCRIBE, '')
        socket.connect(config.get('zmq', 'publisher_addr'))
        while True:
            msg = socket.recv()
            app.latest_message = msg
            # wake up all the waiting requests
            app.waiters_queue.put(StopIteration)
            for ev in app.waiters_queue:
                ev.set()

    gevent.spawn(_process)


@app.route('/')
def index():
    return Response(app.latest_message, content_type='text/plain; charset=utf-8')

@app.route('/longpoll')
def longpoll():
    ev = gevent.event.Event()
    app.waiters_queue.put(ev)
    ev.wait()
    return Response(app.latest_message, content_type='text/plain; charset=utf-8')

if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    app.debug = True
    WSGIServer(('', 8088), app).serve_forever()
else:
    application = app
