import tweepy
from dotenv import load_dotenv
import os as os
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


class TweetManager:
    def __init__(self, tweet_client, post_client):
        self.post_client = post_client
        self.tweet_client = tweet_client

    def send_tweet(self, message):
        try:
            response = self.post_client.create_tweet(text=message)
            if response.data:
                return response.data['id']
            else:
                return 'Error in sending tweet'
        except Exception as e:
            return e.api_messages[0]

    def get_likers(self, tweet_id):
        user_list = []
        for user in tweepy.Paginator(self.tweet_client.get_liking_users, tweet_id, max_results=100).flatten(limit=100):
            user_list.append(user.id)
        return user_list

    def user_info(self, user_id="", user_name=""):
        if user_id != "":
            user_list = self.tweet_client.get_users(ids=user_id,
                                                    user_fields=["public_metrics", "verified", "created_at",
                                                                 "protected",
                                                                 "location", "username", "name",
                                                                 "profile_image_url"]).data
        elif user_name != "":
            user_list = self.tweet_client.get_users(usernames=user_name,
                                                    user_fields=["public_metrics", "verified", "created_at",
                                                                 "protected",
                                                                 "location", "username", "name",
                                                                 "profile_image_url"]).data
        else:
            return "Wrong Parameter"
        if user_list is not None:
            user = user_list[0]
            user_dict = {"id": user.id,
                         "user_name": user.username,
                         "screen_name": user.name,
                         "verified": user.verified,
                         "location": user.location,
                         "created_at": str(user.created_at)
                         }
            return user_dict
        else:
            return "Not Found"

    def get_quoters(self, tweet_id):
        user_list = []
        for tweet in tweepy.Paginator(self.tweet_client.get_quote_tweets, tweet_id, tweet_fields=["author_id"],
                                      max_results=100).flatten(limit=100):
            user_list.append(tweet.author_id)
        return user_list

    def get_retweeters(self, tweet_id):
        user_list = []
        for user in tweepy.Paginator(self.tweet_client.get_retweeters, tweet_id, max_results=100).flatten(limit=100):
            user_list.append(user.id)
        return user_list

    def get_tweet_potentials(self, tweet_id, tweet_count=10000, followers_count=1000):
        retweeter_list = self.get_retweeters(tweet_id)
        qouter_list = self.get_quoters(tweet_id)
        liker_list = self.get_likers(tweet_id)
        potential_retweeters = [x for x in self.user_info(retweeter_list) if x.public_metrics['followers_count'] >
                                followers_count and x.public_metrics['tweet_count'] > tweet_count]
        potential_quoters = [x for x in self.user_info(qouter_list) if x.public_metrics['followers_count'] >
                             followers_count and x.public_metrics['tweet_count'] > tweet_count]
        potential_likers = [x for x in self.user_info(liker_list) if x.public_metrics['followers_count'] >
                            followers_count and x.public_metrics['tweet_count'] > tweet_count]
        return potential_likers, potential_retweeters, potential_quoters

    def get_search_potentials(self, search_term):
        tweet_list = []
        for user in tweepy.Paginator(self.tweet_client.search_recent_tweets, search_term, max_results=100,
                                     tweet_fields=["author_id", "created_at", "geo", "public_metrics"],
                                     expansions=["attachments.media_keys", "attachments.poll_ids", "author_id",
                                                 "entities.mentions.username", "geo.place_id", "in_reply_to_user_id",
                                                 "referenced_tweets.id", "referenced_tweets.id.author_id"],
                                     media_fields=["url"], user_fields=["username"]).flatten(limit=1000):
            tweet_list.append(user.data)
        potentials = [x for x in tweet_list if x["public_metrics"]["retweet_count"] >= -1 or
                      x["public_metrics"]["like_count"] >= 1000]
        return potentials


if __name__ == "__main__":
    tweeter = TweetManager(client, post_client)
    # print(tweeter.get_retweeters(1563613785281007616))
    # print(tweeter.user_info('1556260783826280449'))
    print(tweeter.user_info('1556260783826280449'))
