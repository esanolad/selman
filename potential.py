from dotenv import load_dotenv
import os
import sys
import requests
import time
import argparse
import tweepy

load_dotenv(verbose=True)  # Throws error if no .env file is found
consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")


def get_arguments():
    # Argparse for CLI options. Run `python3 replies.py -h` to see the list of arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tweet_id",
        required=False,
        help="ID of the Tweet for which you want to pull replies",
    )
    # parser.add_argument('integers', metavar='N', type=int, nargs='+',
    # help='an integer for the accumulator')

    parser.add_argument(
        "-s",
        "--start_time",
        help="The oldest UTC timestamp from which the replies will be provided. Format: YYYY-MM-DDTHH:mm:ssZ; for "
             "example: 2021-12-04T01:30:00Z. If unspecified, will default to returning replies from up to 30 days ago.",
    )
    parser.add_argument(
        "-e",
        "--end_time",
        help="The newest, most recent UTC timestamp to which the replies will be provided. Format: YYYY-MM-DDTHH:mm:ssZ; "
             "for example: 2021-12-04T01:30:00Z. If unspecified, will default to [now - 30 seconds].",
    )
    return parser.parse_args()


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FullArchiveSearchPython"
    return r


def get_replies(parameters):
    replies = []

    # search_url = "https://api.twitter.com/2/tweets/search/all"
    search_url = 'https://api.twitter.com/2/tweets/1556406880624410631'
    request_count = 0

    while True:
        response = requests.request(
            "GET", search_url, auth=bearer_oauth, params=parameters
        )
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        response_payload = response.json()
        meta = response_payload["meta"]
        if meta["result_count"] == 0:
            sys.exit("No replies to analyze")
        for reply in response_payload["data"]:
            replies.append(reply)
        request_count += 1
        if "next_token" not in meta:
            break
        next_token = meta["next_token"]
        parameters.update(next_token=next_token)
        time.sleep(1)

    return replies, request_count


def get_twitter_api():
    # authentication of consumer key and secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    # authentication of access token and secret
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api


def process():
    api = get_twitter_api()
    user = api.get_user(screen_name='channelstv')
    # followers = api.followers_ids(api.me().id)
    # followers = api.get_follower_ids()
    # print("Followers", len(followers))
    # friends = api.get_friend_ids()
    # print("You follow:", len(friends))


def follow_tweet_potentials(tweet_id):
    api = get_twitter_api()
    # res=api.get_retweets('1563598379917377536')
    res = api.search_tweets('1563598379917377536')
    return res


def follow_id(id):
    api = get_twitter_api()
    api.create_friendship(id)
    api.get_friend_ids()


if __name__ == "__main__":
    print(follow_tweet_potentials('1562827327414738946'))
    # print(args.end_time)
    # print(get_parameters())
    # parameters, original_tweet_id = get_parameters()

    # replies, request_count = get_replies(parameters)
    # print(replies)
    # print(request_count)

    # api.create_friendship(screen_name='MBuhari')
