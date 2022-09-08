import tweepy
from dotenv import load_dotenv
import os as os
import requests as req


load_dotenv(verbose=True)  # Throws error if no .env file is found

consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
whatsapp_token = "Bearer " + os.getenv("WHATSAPP_BEARER_TOKEN")
client = tweepy.Client(bearer_token)

post_client = tweepy.Client(
    consumer_key=consumer_key, consumer_secret=consumer_secret,
    access_token=access_token, access_token_secret=access_token_secret
)


class Listener(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        print(f"{tweet.id} {tweet.created_at} ({tweet.author_id}): {tweet.text}")
        url = tweet.id
        print("-" * 100)
        rule = self.get_rules().data[0].value
        '''
        mes = send_whatsapp_message('971528183733', rule, url, tweet.text)
        print(mes)
        mes = send_whatsapp_message('2349093478089', rule, url, tweet.text)
        print(mes)
        '''

    def delete_all_rules(self):
        result = self.get_rules()
        if result.data:
            rule_ids = []
            for rule in result.data:
                print(f"rule marked to delete: {rule.id} - {rule.value}")
                rule_ids.append(rule.id)
            if len(rule_ids) > 0:
                self.delete_rules(rule_ids)
            else:
                print("no rules to delete")


def start_stream(rule):
    printer = Listener(bearer_token)
    # printer2 = Listener(bearer_token)
    # printer2.delete_all_rules()
    printer.delete_all_rules()
    rule = tweepy.StreamRule(value=rule)
    printer.add_rules(rule)
    # rule = tweepy.StreamRule(value=rule2)
    # printer2.add_rules(rule)
    printer.filter(expansions="author_id", tweet_fields="created_at")
    # printer2.filter(expansions="author_id", tweet_fields="created_at")


def send_whatsapp_message(number, rule, tweet_id, message):
    url = "https://graph.facebook.com/v14.0/105062785679834/messages"
    headers = {"Accept": "application/json", "Authorization": whatsapp_token}
    my_obj = {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "template",
        "template": {
            "name": "new_message",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": message
                        }
                    ]
                },
                {
                    "type": "header",
                    "parameters": [
                        {
                            "type": "text",
                            "text": rule
                        }
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [
                        {
                            "type": "text",
                            "text": tweet_id
                        }
                    ]
                }
            ]
        }
    }
    return req.post(url, json=my_obj, headers=headers)


if __name__ == '__main__':
    start_stream("obidient")

    # start_stream("from:esanolad_1 OR from:renoomokri")
    # start_stream("IPOB AND Protest AND September AND 2022")
