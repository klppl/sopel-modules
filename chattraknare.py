import sopel
import requests
from sopel.config.types import StaticSection, ValidatedAttribute
from sopel.db import SopelDB
import datetime
from collections import Counter
import logging

class StatsSection(StaticSection):
    db_filename = ValidatedAttribute('db_filename', default='chattraknare.db')

def setup(bot):
    bot.config.define_section('chattraknare', StatsSection)
    try:
        db = SopelDB(bot.config)
        db.execute('''
            CREATE TABLE IF NOT EXISTS wordcounts (
                date TEXT,
                channel TEXT,
                nick TEXT,
                wordcount INTEGER,
                PRIMARY KEY (date, channel, nick)
            )
        ''')
    except Exception as e:
        logging.error(f"Failed to setup database: {e}")
        raise

def get_db(bot):
    try:
        return SopelDB(bot.config)
    except Exception as e:
        logging.error(f"Failed to connect to database: {e}")
        return None

def count_words(bot, trigger):
    # Skip bot commands and triggers
    if trigger.startswith(bot.config.core.prefix):
        return
    
    db = get_db(bot)
    if not db:
        return
        
    try:
        date = datetime.date.today().isoformat()
        channel = trigger.sender
        nick = trigger.nick
        # More sophisticated word counting that excludes URLs and common bot triggers
        words = [w for w in trigger.split() 
                if not w.startswith('http') 
                and not w.startswith(bot.config.core.prefix)]
        wordcount = len(words)
        
        db.execute('''
            INSERT OR REPLACE INTO wordcounts (date, channel, nick, wordcount)
            VALUES (?, ?, ?, COALESCE(
                (SELECT wordcount FROM wordcounts WHERE date = ? AND channel = ? AND nick = ?),
                0
            ) + ?)
        ''', (date, channel, nick, date, channel, nick, wordcount))
    except Exception as e:
        logging.error(f"Failed to count words: {e}")

PERIODS = {
    'idag': 'today',
    'igår': 'yesterday',
    'vecka': 'week',
    'månad': 'month',
    'today': 'today',
    'yesterday': 'yesterday',
    'week': 'week',
    'month': 'month'
}

def get_date_range(period):
    today = datetime.date.today()
    if period == 'today':
        return today, today
    elif period == 'yesterday':
        yesterday = today - datetime.timedelta(days=1)
        return yesterday, yesterday
    elif period == 'week':
        start = today - datetime.timedelta(days=today.weekday())
        return start, start + datetime.timedelta(days=6)
    elif period == 'month':
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year+1, month=1, day=1) - datetime.timedelta(days=1)
        else:
            end = today.replace(month=today.month+1, day=1) - datetime.timedelta(days=1)
        return start, end

@sopel.module.commands('chatt', 'chat')
def show_stats(bot, trigger):
    period = trigger.group(2)
    if not period or period.lower() not in PERIODS:
        bot.reply('Please specify a valid period: idag|igår|vecka|månad / today|yesterday|week|month')
        return
        
    db = get_db(bot)
    if not db:
        bot.reply('Database connection error. Please try again later.')
        return
        
    try:
        period = PERIODS[period.lower()]
        start_date, end_date = get_date_range(period)
        channel = trigger.sender
        
        result = db.execute('''
            SELECT nick, SUM(wordcount) 
            FROM wordcounts 
            WHERE date >= ? AND date <= ? AND channel = ? 
            GROUP BY nick 
            ORDER BY SUM(wordcount) DESC
        ''', (start_date.isoformat(), end_date.isoformat(), channel))
        
        counts = Counter(dict(result.fetchall()))
        if not counts:
            bot.reply(f'No chat statistics available for {period}.')
            return
            
        # Format the output locally instead of using external service
        reply = f'Chat statistics for {period}:\n'
        reply += '\n'.join(f'{nick}: {count}' for nick, count in counts.most_common())
        
        # Split long messages into multiple lines if needed
        max_length = 400  # IRC message length limit
        while reply:
            chunk = reply[:max_length]
            reply = reply[max_length:]
            bot.say(chunk)
            
    except Exception as e:
        logging.error(f"Failed to show stats: {e}")
        bot.reply('An error occurred while retrieving statistics. Please try again later.')
