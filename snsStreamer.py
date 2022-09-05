import pandas as pd
import snscrape.modules.twitter as snstwitter
import snscrape.modules.twitter as twitter
from textblob import TextBlob

import re


def get_tweet_sentiment(text):

    clean_text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w+:\ / \ / \S+)", " ", text).split())
    analysis = TextBlob(clean_text)
    # set sentiment
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

maxTweets = 10
keyword = '#obidient'
tweet_list = []
for i, tweet in enumerate(twitter.TwitterSearchScraper(keyword + ' since:2022-09-01 until:2023-01-01 lang:"en" ')
                                  .get_items()):
    sentiment = get_tweet_sentiment(tweet.content)
    tweet_list.append([str(tweet.id), tweet.date, tweet.user.username, tweet.content, tweet.likeCount,
                       tweet.retweetCount, tweet.replyCount, tweet.user.followersCount, tweet.user.friendsCount,
                       tweet.url, sentiment])
    '''
   
    tweets = {
        "tweet/reply id": "a" + str(tweet.id),
        "inReplyToTweetId": "a" + str(tweet.inReplyToTweetId),
        "conversationId": "a" + str(tweet.conversationId),
        "tweet.username": tweet.user.username,
        "tweet.content": tweet.content,
        "tweet.date": tweet.date,
        "tweet.user.location": tweet.user.location,
        "tweet.likeCount": tweet.likeCount,
        "tweet.replyCount": tweet.replyCount,
        "tweet.retweetCount": tweet.retweetCount,
        "tweet.user.followersCount": tweet.user.followersCount,
        "tweet.user.description": tweet.user.description,
        "tweet.user.friendsCount": tweet.user.friendsCount,
        "tweet.user.statusesCount": tweet.user.statusesCount,
        "tweet.user.favouritesCount": tweet.user.favouritesCount,
        "tweet.user.listedCount": tweet.user.listedCount,
        "tweet.user.mediaCount": tweet.user.mediaCount,
        "tweet.url": tweet.url
    }
    
    '''

    if i == maxTweets:
        break
data_frame = pd.DataFrame(tweet_list, columns=['tweet_id', 'tweet_date', 'username', 'content', 'likes', 'retweets',
                                               'replies', 'user_followers', 'user_friends', 'tweets_url', 'sentiment'])
pd.set_option('display.max_colwidth', None)
print(data_frame)
