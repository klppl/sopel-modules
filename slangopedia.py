import sopel
import requests
from bs4 import BeautifulSoup

@sopel.module.commands('slang')
def slang(bot, trigger):
    ord = trigger.group(2)

    url = f"http://mobil.slangopedia.se/mobil/ordlista/?ord={ord}"

    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')

    try:
        ord = soup.find("h1").text

        definition = soup.find("span", class_="definition").text
        definition = definition[:350]

        bot.say(f"Slangopedia: {definition} (http://www.slangopedia.se/ordlista/?ord={ord})")
    except AttributeError:
        bot.say("Hittar inte ordet")
