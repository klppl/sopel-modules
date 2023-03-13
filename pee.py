from sopel import module

@module.commands('pee')
def pee_alias(bot, trigger):
    nickname = trigger.group(2)
    bot.say("8===D - - -  -")
    bot.say("                 `")
    bot.say("                  '")
    bot.say("                  '")
    bot.say(f"                {nickname}")
