#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-
import twitter
import zmq
import os, re, datetime, ConfigParser

from tools import get_temperature, get_status

config = ConfigParser.RawConfigParser()
config.read(os.environ['CONFIG_FILE'])


ctx = zmq.Context()

def calculate_opened(td):
    hours = int(td.total_seconds() / 3600)
    minutes = int((td.seconds / 60) % 60)

    if hours == 1:
        return "Беше отворен 1 час, %s минути." % minutes

    return "Беше отворен %s часа, %s минути." % (hours, minutes)


def main():
    socket = ctx.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, '')
    socket.connect(config.get('zmq', 'publisher_addr'))
    tweet = twitter.Api(consumer_key=config.get('twitter', 'consumer_key'), access_token_key=config.get('twitter', 'access_token_key'),
            access_token_secret=config.get('twitter', 'access_token_secret'), consumer_secret=config.get('twitter', 'consumer_secret'))

    msg = socket.recv()
    previous_value = get_status(msg)
    time_initial = datetime.datetime.now()

    while True:
        msg = socket.recv()
        current_value = get_status(msg)
        if current_value != previous_value:
            time_of_change = datetime.datetime.now()
            if current_value == 'OPEN':
                time_initial = time_of_change
                tweet.PostUpdate("Хаклабот е отворен. Дојди! http://blog.spodeli.org | %s" % time_of_change.strftime('%d.%m.%Y %H:%M:%S'))
            if current_value == 'CLOSED':
                time_opened  = calculate_opened(time_of_change - time_initial)
                tweet.PostUpdate("Хаклабот е затворен. :-( http://status.spodeli.org | %s" % time_opened)
        previous_value = current_value


if __name__ == '__main__':
    main()
