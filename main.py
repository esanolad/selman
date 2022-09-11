import tweepy
from dotenv import load_dotenv
import os as os
import tweet_manager as t
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

if __name__ == "__main__":

    tweeter = t.TweetManager(bearer_token, consumer_key=consumer_key, consumer_secret=consumer_secret,
                             access_token=access_token, access_token_secret=access_token_secret)

    print(tweeter.get_trends())


    # ttt = tweeter.get_search_potentials("obidient")
    # new_list, tweet_list, quoted_list = t.process_tweets(ttt)
    # for k in quoted_list:
    #     print(k)

    # print(tweeter.get_retweeters(1563613785281007616))
    # print(tweeter.user_info(user_name="esanolad_1"))
