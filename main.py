from flask import Flask, request, send_file, make_response
from os import getenv
from twilio import twiml
import tweepy
import time
import random
import string

app = Flask("tweetspeak")

# credentials
API_KEY = getenv("TWEETSPEAK_API_KEY")
API_SECRET = getenv("TWEETSPEAK_API_SECRET")
ACCESS_TOKEN = getenv("TWEETSPEAK_ACCESS_TOKEN")
ACCESS_SECRET = getenv("TWEETSPEAK_ACCESS_SECRET")

@app.route("/")
def index():
    return "get out"

@app.route("/hook/", methods={"GET", "POST"})
def twilio_resp():
    if request.method == "GET":
        r = twiml.Response()
        r.say(get_tweet())
        r.gather(numDigits=1, timeout=5)
        return r.toxml(), {"Content-Type": "text/xml"}
    elif request.method == "POST":
        r = twiml.Response()
        print(request.values.get("Digits"))
        if('*' in request.values.get('Digits', '')):
            r.say("thanks!")
        return r.toxml(), {"Content-Type": "text/xml"}

tweets=[]
tweets_timestamp=0

def get_tweet():
    global tweets, tweets_timestamp
    now = time.time()
    if(now - tweets_timestamp > 300):
        tweets = twitter.user_timeline("codl", count=500)
        # filter out replies
        tweets = filter(lambda t: not t.in_reply_to_status_id, tweets)
        # filter out media
        tweets = filter(lambda t: not hasattr(t, "media"), tweets)
        # filter out links
        tweets = filter(lambda t: not "https://t.co" in t.text, tweets)
        # filter out tweets with no alphanum characters
        tweets = filter(lambda t:
            any((char in t.text for char in string.ascii_letters + string.digits))
        , tweets)
        tweets = list(tweets)
        tweets.sort(key=lambda t: t.favorite_count, reverse=True)
        tweets = tweets[:40]
        tweets_timestamp = now
    tweet = random.choice(tweets)
    return tweet.text

twitter = None

def setup_twitter():
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

    global twitter
    twitter = tweepy.API(auth)


app.before_first_request(setup_twitter)

if __name__ == "__main__":
    if any([var == None for var in (API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)]):
        print("set your env vars!!!")
        exit(1)

    app.run(host="10.7.0.1")
