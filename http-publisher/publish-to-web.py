# run with 
# uwsgi --plugins python,gevent --gevent 1000 --http-socket :5001 --wsgi-file ...

ADDR = "tcp://192.168.88.49:5556"

import zmq.green as zmq
ctx = zmq.Context()

def application(env, start_response):
    socket = ctx.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, '')
    socket.connect(ADDR)
    msg = socket.recv()

    status = '200 OK'
    response_headers = [('Content-type','text/plain')]
    start_response(status, response_headers)

    return [msg]

if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    WSGIServer(('', 8088), application).serve_forever()