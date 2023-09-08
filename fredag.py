from sopel import module
import re
import datetime

@module.rule('.*')
def fredag(bot, trigger):
    question = trigger.group(0)
    if re.search(r"är\s+det\s+fredag\??", question, re.IGNORECASE):
        today = datetime.datetime.today().weekday()
        if today == 4: 
            bot.say('JA! https://rebecca.blackfriday')
        else:
            bot.say('NEJ, det är inte fredag.')
