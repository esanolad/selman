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


def send_tweet(message):
    try:
        response = post_client.create_tweet(text=message)
        if response.data:
            return response.data['id']
        else:
            print('Error in sending tweet')
    except Exception as e:
        return e.api_messages[0]


def user_info(user_id):
    return client.get_users(ids=user_id, user_fields=["public_metrics", "verified", "created_at", "protected",
                                                      "location", "username", "name", "profile_image_url"]).data


def user_id(user_name):
    return client.get_users(usernames=user_name, user_fields=["public_metrics", "verified", "created_at", "protected",
                                                             "location", "username", "name", "profile_image_url"]).data


def get_likers(tweet_id):
    user_list = []
    for user in tweepy.Paginator(client.get_liking_users, tweet_id, max_results=100).flatten(limit=100):
        user_list.append(user.id)
    return user_list


def get_quoters(tweet_id):
    user_list = []
    for tweet in tweepy.Paginator(client.get_quote_tweets, tweet_id, tweet_fields=["author_id"],
                                  max_results=100).flatten(limit=100):
        user_list.append(tweet.author_id)
    return user_list


def get_retweeters(tweet_id):
    user_list = []
    for user in tweepy.Paginator(client.get_retweeters, tweet_id, max_results=100).flatten(limit=100):
        user_list.append(user.id)
    return user_list


def get_tweet_potentials(tweet_id):
    retweeter_list = get_retweeters(tweet_id)
    qouter_list = get_quoters(tweet_id)
    liker_list = get_likers(tweet_id)
    potential_retweeters = [x for x in user_info(retweeter_list) if x.public_metrics['followers_count'] > 1000
                            and x.public_metrics['tweet_count'] > 10000]
    potential_quoters = [x for x in user_info(qouter_list) if x.public_metrics['followers_count'] > 1000
                         and x.public_metrics['tweet_count'] > 10000]
    potential_likers = [x for x in user_info(liker_list) if x.public_metrics['followers_count'] > 1000
                        and x.public_metrics['tweet_count'] > 10000]
    return potential_likers, potential_retweeters, potential_quoters


def get_search_potentials(search_term):
    tweet_list = []
    for user in tweepy.Paginator(client.search_recent_tweets, search_term, max_results=100,
                                 tweet_fields=["author_id", "created_at", "geo", "public_metrics"],
                                 expansions=["attachments.media_keys", "attachments.poll_ids", "author_id",
                                             "entities.mentions.username", "geo.place_id", "in_reply_to_user_id",
                                             "referenced_tweets.id", "referenced_tweets.id.author_id"],
                                 media_fields=["url"], user_fields=["username"]).flatten(limit=1000):
        tweet_list.append(user.data)
    potentials = [x for x in tweet_list if x["public_metrics"]["retweet_count"] >= -1 or
                  x["public_metrics"]["like_count"] >= 1000]
    # for i in range(len(potentials)):
    # user = user_info(potentials[i]['author_id'])[0]
    # potentials[i]['author_metrics'] = user.public_metrics
    # potentials[i]['author_username'] = user.username
    return potentials


def check_dict_in_list(tweet_list, item):
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


def filter_main(dict_list):
    new_list = []
    tweet_list = []
    for item in dict_list:
        if "referenced_tweets" in item.keys():
            ff = item["referenced_tweets"][0]
            if check_dict_in_list(new_list, ff):
                pass
            else:
                if 'entities' in item.keys():
                    new_list.append(item)  # referenced_tweet has not been added to the list,
                    main_tweet = {'author_id': item['entities']['mentions'][0]['id'],
                                  'username': item['entities']['mentions'][0]['username'],
                                  'tweet_id': item["referenced_tweets"][0]['id'],
                                  'retweet_count': item['public_metrics']['retweet_count']}
                    tweet_list.append(main_tweet)
                else:  # for quoted tweets and replied tweet
                    pass  # TODO: handle quoted and reply tweets
        else:  # for now discard tweets without retweets
            pass  # TODO: handle tweets that are not retweeted
    new_list.sort(key=lambda x: x['public_metrics']['retweet_count'], reverse=True)
    tweet_list.sort(key=lambda x: x['retweet_count'], reverse=True)
    return new_list, tweet_list


if __name__ == "__main__":
    print(user_info("1556260783826280449"))
    print(user_id("esanolad_1"))
    # result = json.dumps(result[0], indent=3)

    # print(result[0]['text'])
    ''' 
    c = 1
    print("SN   DATE   TWEET_ID   TWEET AUTHOR  RETWEETS  LIKES  FOLLOWERS TEXT ")
    for res in result:
        print("{}   {}  {}   {}   {}      {}  {}".format(
            c, res['created_at'], res['id'], res['author_id'], res['public_metrics']['retweet_count'],
            res['public_metrics']['like_count'], res['text']))
        c += 1

    # print(user_info(1288431166840885248)[0].public_metrics)
 
    
    like, ret, qou = get_tweet_potentials(1563613785281007616)
    print("Like Potential")
    for pot in like:
        print(pot.id, pot.username, pot.public_metrics, pot.verified, pot.created_at)
    print("retweet potential")
    for pot in ret:
        print(pot.id, pot.username, pot.public_metrics, pot.verified, pot.created_at)
    print("Quote Potentials")
    for pot in qou:
        print(pot.id, pot.username, pot.public_metrics, pot.verified, pot.created_at)
'''
