import re

import tweepy


def check_referenced_tweets_in_tweet_list(tweet_list, item):
    flag = False
    for c in tweet_list:
        try:
            if item == c["referenced_tweets"][0]:
                flag = True
                break
        except KeyError:  # ignore items in the list that do not have referenced_tweets
            flag = True
            break
    return flag


def check_tweet_id_in_tweet_list(tweet_list, item):
    for c in tweet_list:
        try:
            if item == c["referenced_tweets"][0]['id']:
                text = c['text']
                return text[text.index(':') + 1:]  # return text without the RT @ username

        except KeyError:  # ignore items in the list that do not have referenced_tweets
            break
    return False


def process_tweets(dict_list):
    """

    param dict_list: List of searched tweet result
    :return: a tuple containing three lists:
        - new_list which is a sublist of the main list with duplicate retweets removed
        - tweet_list is the list of dictionaries with unique retweets
        - original_quoted_replied_list is the list of dictionaries with replied, quoted and original tweets
    """
    new_list = []
    tweet_list = []
    original_quoted_replied_list = []
    for item in dict_list:
        if "referenced_tweets" in item.keys():  # check if the tweet is a referenced tweet
            ff = item["referenced_tweets"][0]
            if check_referenced_tweets_in_tweet_list(new_list, ff):
                # check if this tweet has been added to the new list and do nothing
                pass
            else:
                if 'entities' in item.keys():  # check if the tweet is a retweet
                    new_list.append(item)  # referenced_tweet has not been added to the list,
                    main_tweet = {'author_id': item['entities']['mentions'][0]['id'],
                                  'username': item['entities']['mentions'][0]['username'],
                                  'tweet_id': item["referenced_tweets"][0]['id'],
                                  'retweet_count': item['public_metrics']['retweet_count']}
                    tweet_list.append(main_tweet)
                elif item['referenced_tweets'][0]['type'] == "quoted":
                    new_list.append(item)
                    main_tweet = {'author_id': item['author_id'],
                                  'username': "", 'ref_tweet': item['referenced_tweets'][0]['id'],
                                  'tweet_id': item['id'], "text": item['text'], "type": "quoted",
                                  'retweet_count': item['public_metrics']['retweet_count']}
                    original_quoted_replied_list.append(main_tweet)
                elif item['referenced_tweets'][0]['type'] == "replied_to":
                    new_list.append(item)
                    main_tweet = {'author_id': item['author_id'],
                                  'username': "", 'ref_tweet': item['referenced_tweets'][0]['id'],
                                  'tweet_id': item['id'], "text": item['text'], "type": "replied_to",
                                  'retweet_count': item['public_metrics']['retweet_count']}
                    original_quoted_replied_list.append(main_tweet)
                else:  # for  replied tweet
                    print(item)  # unknown tweet type
        else:  # original tweets
            new_list.append(item)
            main_tweet = {'author_id': item['author_id'],
                          'username': "", 'ref_tweet': "",
                          'tweet_id': item['id'], "text": item['text'], "type": "original",
                          'retweet_count': item['public_metrics']['retweet_count']}
            original_quoted_replied_list.append(main_tweet)
    new_list.sort(key=lambda x: x['public_metrics']['retweet_count'], reverse=True)
    tweet_list.sort(key=lambda x: x['retweet_count'], reverse=True)
    return new_list, tweet_list, original_quoted_replied_list


class TweetManager:
    def __init__(self, bearer_token, consumer_key="", consumer_secret="",
                 access_token="", access_token_secret=""):

        """
        :param bearer_token:
        :param consumer_key:
        :param consumer_secret:
        :param access_token:
        :param access_token_secret:
        """
        self.tweet_client = tweepy.Client(bearer_token)
        self.post_client = tweepy.Client(
            consumer_key=consumer_key, consumer_secret=consumer_secret,
            access_token=access_token, access_token_secret=access_token_secret
        )
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

    def send_tweet(self, message):
        try:
            response = self.post_client.create_tweet(text=message)
            if response.data:
                return response.data['id']
            else:
                return 'Error in sending tweet'
        except Exception as e:
            return e.api_messages[0]

    def get_tweet_text(self, tweet_id):
        return self.tweet_client.get_tweet(tweet_id).data

    def get_my_timeline(self):
        res = self.post_client.get_home_timeline()
        if res.data:
            return res.data[0]

    def create_list(self):
        return self.post_client.create_list('national', private=True)

    def get_list(self, list_id):
        # list_id='1569171375193030657'

        return self.tweet_client.get_list(list_id)

    def get_likers(self, tweet_id):
        user_list = []
        for user in tweepy.Paginator(self.tweet_client.get_liking_users, tweet_id, max_results=10).flatten(limit=10):
            user_list.append(user.id)
        return self.users_info(user_list)

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
                         "created_at": str(user.created_at),
                         "image_url": user.profile_image_url,
                         "followers_count": user.public_metrics["followers_count"],
                         "following_count": user.public_metrics["following_count"],
                         "tweet_count": user.public_metrics["tweet_count"],
                         "listed_count": user.public_metrics["listed_count"]
                         }
            return user_dict
        else:
            return "Not Found"

    def users_info(self, users_list):
        users = []
        users_id_list = self.tweet_client.get_users(ids=users_list,
                                                    user_fields=["public_metrics", "verified", "created_at",
                                                                 "protected",
                                                                 "location", "username", "name",
                                                                 "profile_image_url"]).data
        if users_id_list is not None:
            for user in users_id_list:
                user_dict = {"id": user.id,
                             "user_name": user.username,
                             "screen_name": user.name,
                             "verified": user.verified,
                             "location": user.location,
                             "created_at": str(user.created_at),
                             "image_url": user.profile_image_url,
                             "followers_count": user.public_metrics["followers_count"],
                             "following_count": user.public_metrics["following_count"],
                             "tweet_count": user.public_metrics["tweet_count"],
                             "listed_count": user.public_metrics["listed_count"]
                             }
                users.append(user_dict)
            return users
        else:
            return "Not Found"

    def get_quoters(self, tweet_id):
        user_list = []
        for tweet in tweepy.Paginator(self.tweet_client.get_quote_tweets, tweet_id, tweet_fields=["author_id"],
                                      max_results=100).flatten(limit=100):
            user_list.append(tweet.author_id)
        return self.users_info(user_list)

    def get_retweeters(self, tweet_id):
        user_list = []
        for user in tweepy.Paginator(self.tweet_client.get_retweeters, tweet_id, max_results=10).flatten(limit=10):
            user_list.append(user.id)
        return self.users_info(user_list)

    def get_tweet_influencers(self, tweet_id, tweet_count=10000, followers_count=1000):
        retweeter_list = self.get_retweeters(tweet_id)
        qouter_list = self.get_quoters(tweet_id)
        liker_list = self.get_likers(tweet_id)
        potential_retweeters = [user for user in retweeter_list if user['followers_count'] >
                                followers_count and user['tweet_count'] > tweet_count]
        potential_quoters = [user for user in qouter_list if user['followers_count'] >
                             followers_count and user['tweet_count'] > tweet_count]
        potential_likers = [user for user in liker_list if user['followers_count'] >
                            followers_count and user['tweet_count'] > tweet_count]
        return potential_likers, potential_retweeters, potential_quoters

    def get_search_raw(self, search_term):
        tweet_list = []
        try:
            for user in tweepy.Paginator(self.tweet_client.search_recent_tweets, search_term, max_results=100,
                                         tweet_fields=["author_id", "created_at", "geo", "public_metrics"],
                                         expansions=["attachments.media_keys", "attachments.poll_ids", "author_id",
                                                     "entities.mentions.username", "geo.place_id",
                                                     "in_reply_to_user_id",
                                                     "referenced_tweets.id", "referenced_tweets.id.author_id"],
                                         media_fields=["url"], user_fields=["username"]).flatten(limit=3000):
                tweet_list.append(user.data)
            return tweet_list
        except Exception as e:  # handles to many request
            print(e)  # logs this error
            return "wait"

    def get_search_potentials(self, search_term):
        tweet_list = []
        try:

            for user in tweepy.Paginator(self.tweet_client.search_recent_tweets, search_term, max_results=100,
                                         tweet_fields=["author_id", "created_at", "geo", "public_metrics"],
                                         expansions=["attachments.media_keys", "attachments.poll_ids", "author_id",
                                                     "entities.mentions.username", "geo.place_id",
                                                     "in_reply_to_user_id",
                                                     "referenced_tweets.id", "referenced_tweets.id.author_id"],
                                         media_fields=["url"], user_fields=["username"]).flatten(limit=1000):
                tweet_list.append(user.data)
            potentials = [x for x in tweet_list if x["public_metrics"]["retweet_count"] >= 10 or
                          x["public_metrics"]["like_count"] >= 1000]
            return potentials
        except Exception as e:  # handles to many request
            print(e)  # logs this error
            return "wait"

    def get_trends(self, woeid=23424908):
        result: [] = self.api.get_place_trends(id=woeid)
        trends = result[0]['trends']
        # filtered_trend = list(filter(lambda trend: trend['tweet_volume'] is not None, trends))
        # filtered_trend_none = filter(lambda trend: trend['tweet_volume'] is None, trends)

        return trends




if __name__ == "__main__":
    pass
