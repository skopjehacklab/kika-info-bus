#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-
import twitter
import zmq
import os, re, datetime, ConfigParser


config = ConfigParser.RawConfigParser()
config.read(os.environ['CONFIG_FILE'])


ctx = zmq.Context()

def get_value(msg):
    match = re.search(r'\b(OPEN|CLOSED)\b', msg)
    return match.group(1)

def main():
    socket = ctx.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, '')
    socket.connect(config.get('zmq', 'publisher_addr'))
    tweet = twitter.Api(consumer_key=config.get('twitter', 'consumer_key'), access_token_key=config.get('twitter', 'access_token_key'),
            access_token_secret=config.get('twitter', 'access_token_secret'), consumer_secret=config.get('twitter', 'consumer_secret'))

    msg = socket.recv()
    previous_value = get_value(msg)
    while True:
        msg = socket.recv()
        current_value = get_value(msg)
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if current_value != previous_value:
            if current_value == 'OPEN':
                tweet.PostUpdate("Хаклабот е отворен. Дојди! http://blog.spodeli.org | %s" % now)
            if current_value == 'CLOSED':
                tweet.PostUpdate("Хаклабот е затворен. :-( http://status.spodeli.org | %s" % now)
        previous_value = current_value


if __name__ == '__main__':
    main()
