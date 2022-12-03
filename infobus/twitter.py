from __future__ import print_function

import twitter
import os


def twitter_init():
    consumer_key = os.environ['TWITTER_CONSUMER_KEY']
    consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
    access_token_key = os.environ['TWITTER_ACCESS_TOKEN_KEY']
    access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

    tweet = twitter.Api(consumer_key=consumer_key, access_token_key=access_token_key,
            access_token_secret=access_token_secret, consumer_secret=consumer_secret)
    return tweet

def twitter_update_status(client, userdata, msg):
    tweet = twitter_init()

    current_value =
    time_of_change =

    if current_value == 'OPEN':
        time_initial = time_of_change
        tweet.PostUpdate("Хаклабот е отворен. Дојди! https://kika.spodeli.org | %s" % time_of_change.strftime('%d.%m.%Y %H:%M:%S'))
    if current_value == 'CLOSED':
        time_opened  = calculate_opened(time_of_change - time_initial)
        tweet.PostUpdate("Хаклабот е затворен. :-( http://status.spodeli.org | %s" % time_opened)


def calculate_opened(td):
    hours = int(td.total_seconds() / 3600)
    minutes = int((td.seconds / 60) % 60)

    if hours == 1:
        return "Беше отворен 1 час, %s минути." % minutes

    return "Беше отворен %s часа, %s минути." % (hours, minutes)
