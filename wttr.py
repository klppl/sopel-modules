import sopel
import requests

@sopel.module.commands('wttr', 'weather')
def weather(bot, trigger):
    city = trigger.group(2)
    city = city.strip()

    if not city:
        bot.say("Du glömde att ange en stad.")
        return
    url_with_sun = f"https://wttr.in/{city}?lang=sv&format=%l:%c+%C+Temp+%t+Luftfuktighet:+%h+UV:+%u++Soluppgång:+%S+%m+Solnedgång:+%s"
    url_without_sun = f"https://wttr.in/{city}?lang=sv&format=%l:%c+%C+Temp+%t+Luftfuktighet:+%h+UV:+%u"
    response = requests.get(url_with_sun)
    
    if response.status_code != 200:
        response = requests.get(url_without_sun)
        
    if response.status_code == 200:
        bot.say(response.text + " | [https://wttr.in/" + city + ".png?lang=sv]")
    else:
        bot.say("Något gick fel.")
