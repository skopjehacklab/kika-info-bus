# run with
# uwsgi --plugins python,gevent --gevent 1000 --http-socket :5001 --wsgi-file ...

from flask import Flask, Response
import zmq.green as zmq
import gevent
import os, ConfigParser

config = ConfigParser.RawConfigParser()
config.read(os.environ['CONFIG_FILE'])

ctx = zmq.Context()

app = Flask(__name__)

@app.before_first_request
def run():
    app.latest_message = None
    def _process():
        socket = ctx.socket(zmq.SUB)
        socket.setsockopt(zmq.SUBSCRIBE, '')
        socket.connect(config.get('zmq', 'publisher_addr'))
        while True:
            msg = socket.recv()
            app.latest_message = msg

    gevent.spawn(_process)


@app.route('/')
def index():
    return Response(app.latest_message, content_type='text/plain; charset=utf-8')

if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    WSGIServer(('', 8088), app).serve_forever()
else:
    application = app
