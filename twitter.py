from sopel import module
from tweety import Twitter
import re

username = "username"
password = "password"

DOMAIN_REGEX = r"https?://(?:m(?:obile)?\.)?(?:twitter|x)\.com/([\w\d]+)/status/(\d+)"

app = Twitter("your_session_info")
app.start(username, password)

def guess_media_link(item):

    variants = item.get('streams', [])

    if not variants:
        return item['media_url_https']

    variants.sort(key=lambda k: k.get('bitrate', 0))

    return variants[-1]['url']

@module.rule(DOMAIN_REGEX)
def fetch_tweet(bot, trigger):
    tweet_url = trigger.group(0)
    
    try:
        tweet = app.tweet_detail(tweet_url)
        message = f"@{tweet['author']['username']}: {tweet['text']}"

        if 'media' in tweet: 
            for item in tweet['media']:
                media_link = guess_media_link(item)
                message += f" [media: {media_link}]"

        bot.say(message)
    except Exception as e:
        bot.say("Sorry, I couldn't fetch the tweet details.")
