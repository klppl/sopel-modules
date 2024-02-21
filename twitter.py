from sopel import module
from tweety import Twitter
import re

username = "username"
password = "password"

DOMAIN_REGEX = r"https?://(?:m(?:obile)?\.)?(?:twitter|x)\.com/([\w\d]+)/status/(\d+)"

app = Twitter("your_session_info")
app.start(username, password)

@module.rule(DOMAIN_REGEX)
def fetch_tweet(bot, trigger):

    tweet_url = trigger.group(0)

    try:
        tweet = app.tweet_detail(tweet_url)

      message = f"Tweet: {tweet['text']}"
        bot.say(message)
    except Exception as e:
        bot.say("Sorry, I couldn't fetch the tweet details.")
