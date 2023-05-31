import sopel
import requests
from sopel.config.types import StaticSection, ValidatedAttribute
from sopel.db import SopelDB
import datetime
from collections import Counter

class StatsSection(StaticSection):
    db_filename = ValidatedAttribute('db_filename', default='chattraknare.db')

def setup(bot):
    bot.config.define_section('chattraknare', StatsSection)
    db = SopelDB(bot.config)
    db.execute('CREATE TABLE IF NOT EXISTS wordcounts (date TEXT, channel TEXT, nick TEXT, wordcount INTEGER)')

@sopel.module.rule('.*')
def count_words(bot, trigger):
    db = SopelDB(bot.config)
    date = datetime.date.today().isoformat()
    channel = trigger.sender
    nick = trigger.nick
    wordcount = len(trigger.split())
    db.execute('INSERT INTO wordcounts (date, channel, nick, wordcount) VALUES (?, ?, ?, ?)',
               (date, channel, nick, wordcount))

@sopel.module.commands('chatt', 'chat')
def show_stats(bot, trigger):
    period = trigger.group(2)
    if period not in ['idag', 'igår', 'vecka', 'månad', 'today', 'yesterday', 'week', 'month']:
        bot.reply('ah ah ah you didnt say the magic word... idag|igår|vecka|månad / today|yesterday|week|month')
        return
    db = SopelDB(bot.config)
    channel = trigger.sender
    if period == 'idag' or period == 'today':
        date = datetime.date.today().isoformat()
    elif period == 'igår' or period == 'yesterday':
        date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    elif period == 'vecka' or period == 'week':
        date = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    elif period == 'månad' or period == 'month':
        date = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    result = db.execute('SELECT nick, SUM(wordcount) FROM wordcounts WHERE date >= ? AND channel = ? GROUP BY nick ORDER BY SUM(wordcount) DESC',
                        (date, channel))
    counts = Counter(dict(result.fetchall()))

    reply = '\n'.join(f'{nick}: {count}' for nick, count in counts.most_common())
    reply = reply.encode("utf-8")
    response = requests.post("https://dumpinen.com", data=reply)
    chattraknare_output = response.text

    bot.say(chattraknare_output)
