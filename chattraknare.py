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
    today = datetime.date.today()
    if period == 'idag' or period == 'today':
        start_date = today
        end_date = today
    elif period == 'igår' or period == 'yesterday':
        start_date = today - datetime.timedelta(days=1)
        end_date = start_date
    elif period == 'vecka' or period == 'week':
        start_date = today - datetime.timedelta(days=today.weekday())
        end_date = start_date + datetime.timedelta(days=6)
    elif period == 'månad' or period == 'month':
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year+1, month=1, day=1) - datetime.timedelta(days=1)
        else:
            end_date = today.replace(month=today.month+1, day=1) - datetime.timedelta(days=1)
    result = db.execute('SELECT nick, SUM(wordcount) FROM wordcounts WHERE date >= ? AND date <= ? AND channel = ? GROUP BY nick ORDER BY SUM(wordcount) DESC',
                        (start_date.isoformat(), end_date.isoformat(), channel))
    counts = Counter(dict(result.fetchall()))

    reply = '\n'.join(f'{nick}: {count}' for nick, count in counts.most_common())
    reply = reply.encode("utf-8")
    response = requests.post("https://dumpinen.com", data=reply)
    chattraknare_output = response.text

    bot.say(chattraknare_output)
