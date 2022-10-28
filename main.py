import re
from textblob import TextBlob
import tweepy
from dotenv import load_dotenv
import os as os
import tweet_manager as t
import time as time
from elasticsearch import Elasticsearch, helpers
from datetime import timedelta, datetime
import json as json

load_dotenv(verbose=True)  # Throws error if no .env file is found

consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

client = tweepy.Client(bearer_token)

post_client = tweepy.Client(
    consumer_key=consumer_key, consumer_secret=consumer_secret,
    access_token=access_token, access_token_secret=access_token_secret
)


def get_nlp(tweet):
    tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
    analysis = TextBlob(tweet)
    if analysis.sentiment.polarity > 0:
        sentiment = 'positive'
    elif analysis.sentiment.polarity == 0:
        sentiment = 'neutral'
    else:
        sentiment = 'negative'

    return sentiment






def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
            + timedelta(hours=t.minute // 30))


def keep():
    es = Elasticsearch(hosts=os.getenv("ELASTIC"), ca_certs="http_ca.crt",
                       basic_auth=("elastic", os.getenv("ELASTIC_PASSWORD"))
                       )
    tweeter = t.TweetManager(bearer_token, consumer_key=consumer_key, consumer_secret=consumer_secret,
                             access_token=access_token, access_token_secret=access_token_secret)
    result = {}
    trends = tweeter.get_trends()

    for trend_item in trends:
        # searches each trend item get tweets with good retweets from them
        tw = tweeter.get_search_potentials(trend_item["name"])
        if tw == "wait":
            print("waiting for 15 minutes")
            time.sleep(60 * 10)
            tw = tweeter.get_search_potentials(trend_item["name"])

        new_list, tweet_list, original_quoted_replied_list = t.process_tweets(tw)

        process_list = []
        for item in tweet_list:
            # tweet_text = str(tweeter.get_tweet_text(item['tweet_id']))
            tweet_text = t.check_tweet_id_in_tweet_list(new_list, item['tweet_id'])
            if tweet_text:
                item['tweet_text'] = tweet_text
                item['trend_name'] = trend_item["name"]
                item['time_stamp'] = hour_rounder(datetime.now())
                res = es.index(
                    index='daily_trends',
                    document=item
                )
                print(res)
            else:
                continue
                # tweet_text = str(tweeter.get_tweet_text(item['tweet_id']))
                # item['tweet_text'] = tweet_text
                # time.sleep(0.1)
            process_list.append(item)
            # print(item)

            time.sleep(0.01)
        print("Trend text ", trend_item)
        # result['trend'] = trend_item
        # result['trend_data'] = process_list

        print("*" * 100)
        # time.sleep(15*60)   #wait for 15 minutes to take care of twitter rate limits


def keep2():
    es = Elasticsearch(hosts=os.getenv("ELASTIC"), ca_certs="http_ca.crt",
                       basic_auth=("elastic", os.getenv("ELASTIC_PASSWORD"))
                       )
    tweeter = t.TweetManager(bearer_token, consumer_key=consumer_key, consumer_secret=consumer_secret,
                             access_token=access_token, access_token_secret=access_token_secret)

    trends = tweeter.get_trends()

    for trend_item in trends:
        print(trend_item)
        trend_item['time_stamp'] = hour_rounder(datetime.now())
        res = es.index(
            index='daily_trends',
            document=trend_item
        )
        print("Getting each tweet")
        term = trend_item["name"] + " -is:retweet -is:reply -is:quote"  # original tweet
        term = term.replace(' and ', ' \"and\" ')  # replacing and with "and"
        term = term.replace(' or ', ' \"or\" ')  # replacing or with "or"
        term = term.replace(' AND ', ' \"AND\" ')  # replacing and with "and"
        term = term.replace(' OR ', ' \"OR\" ')  # replacing or with "or"
        term = term.replace(' & ', ' \"&\" ')  # replacing &
        tw = tweeter.get_search_raw(term)
        if tw == "wait":
            print("waiting for 15 minutes")
            time.sleep(60 * 10)
            tw = tweeter.get_search_raw(trend_item["name"])
        # sends
        for item in tw:
            time.sleep(0.01)
            print(item["text"])
            item['time_stamp'] = hour_rounder(datetime.now())
            item['trend_name'] = trend_item["name"]
            item['sentiment'] = get_nlp(item["text"])
            try:
                res = es.index(
                    index='original_new',
                    document=item
                )
            except Exception as e:
                # logs the exception
                print(e)

        print("*" * 100)


if __name__ == "__main__":
    keep2()

    # tw = tweeter.get_search_raw('beauty said or love light -is:retweet -is:reply -is:quote')
