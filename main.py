from flask import Flask, request, send_file, make_response, render_template
from os import getenv
from twilio import twiml
import twitter
import time
import random
import string
import requests

app = Flask("tweetspeak")

# credentials
API_KEY = getenv("TWEETSPEAK_API_KEY")
API_SECRET = getenv("TWEETSPEAK_API_SECRET")
ACCESS_TOKEN = getenv("TWEETSPEAK_ACCESS_TOKEN")
ACCESS_SECRET = getenv("TWEETSPEAK_ACCESS_SECRET")

NUMBERS = [ ]

@app.route("/")
def index():
    beacon("/diala/visit")
    return render_template("index.html", numbers=NUMBERS)

@app.route("/hook/", methods={"POST"})
def twilio_resp_hook():
    tweet = get_tweet()
    beacon("/diala/call",
            tweet=tweet['id_str'],
            number=request.values.get("To"),
            from_country=request.values.get("FromCountry"))
    r = twiml.Response()
    r.say(tweet['text'])
    r.gather(numDigits=1, timeout=5, action="/fave/%s" % (tweet['id_str'],))
    return r.toxml(), {"Content-Type": "text/xml"}

@app.route("/fave/<id>", methods={"POST"})
def twilio_resp_fave(id):
    beacon("/diala/fave",
            tweet=id,
            number=request.values.get("To"),
            from_country=request.values.get("FromCountry"))
    r = twiml.Response()
    if('*' in request.values.get('Digits', '')):
        r.say("thanks!")
    return r.toxml(), {"Content-Type": "text/xml"}

tweets=[]
tweets_timestamp=0

def get_tweet():
    global tweets, tweets_timestamp
    now = time.time()
    if(now - tweets_timestamp > 300):
        uid = tw.account.verify_credentials()['id']
        tweets = tw.statuses.user_timeline(user_id=uid, count=200, include_rts=False)
        # filter out replies
        tweets = filter(lambda t: not t['in_reply_to_status_id'], tweets)
        # filter out media
        tweets = filter(lambda t: not "media" in t, tweets)
        # filter out links
        tweets = filter(lambda t: not "https://t.co" in t['text'], tweets)
        # filter out tweets with no alphanum characters
        tweets = filter(lambda t:
            any((char in t['text'] for char in string.ascii_letters + string.digits))
        , tweets)
        tweets = list(tweets)
        tweets.sort(key=lambda t: t['favorite_count'], reverse=True)
        tweets = tweets[:40]
        tweets_timestamp = now
    tweet = random.choice(tweets)
    return tweet

rs = requests.Session()
def beacon(url, **kwargs):
    try:
        rs.post("https://beacon.codl.fr%s" % (url,), json = kwargs)
    except Exception:
        pass


tw = None

def setup_twitter():
    global tw
    tw = twitter.Twitter(auth=twitter.OAuth(
        ACCESS_TOKEN, ACCESS_SECRET, API_KEY, API_SECRET))


app.before_first_request(setup_twitter)

if __name__ == "__main__":
    if any([var == None for var in (API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)]):
        print("set your env vars!!!")
        exit(1)

    app.run(host=getenv("TWEETSPEAK_HOST","127.0.0.1"), port=int(getenv("TWEETSPEAK_PORT", "5000")))
