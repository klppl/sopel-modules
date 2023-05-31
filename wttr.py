import sopel
import requests


@sopel.module.commands('wttr', 'weather')
def weather(bot, trigger):
    city = trigger.group(2)
    city = city.strip()

    if not city:
        bot.say("Du glömde att ange en stad.")
        return
    url = f"https://wttr.in/{city}?lang=sv&format=%l:%c+%C+Temp+%t+Luftfuktighet:+%h+UV:+%u++Soluppgång:+%S+%m+Solnedgång:+%s"
    response = requests.get(url)
    if response.status_code == 200:
        bot.say(response.text + " | [https://wttr.in/" + city + ".png?lang=sv]")
    else:
        bot.say("Något gick fel.")
