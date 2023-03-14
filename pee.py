from sopel import module
from sopel import formatting

@module.commands('pee')
def pee_alias(bot, trigger):
    nickname = trigger.group(2)
    bot.say(formatting.color("8===D", "orange") + formatting.color("~~ ~", "yellow"))
    bot.say(formatting.color("                 `", "yellow"))
    bot.say(formatting.color("                  '", "yellow"))
    bot.say(formatting.color("                  '", "yellow"))
    bot.say(formatting.color("                " + nickname, "blue"))
