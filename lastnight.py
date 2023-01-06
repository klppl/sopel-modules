import sopel
import requests
from bs4 import BeautifulSoup

@sopel.module.commands('lastnight')
def lastnight(bot, trigger):
    # Fetch the data from the web
    r = requests.get('https://lastnight.in/sweden/')
    soup = BeautifulSoup(r.text, 'html.parser')
    days = soup.find('strong').text.strip()

    # Reply with the data
    bot.say(f'It has been {days} day(s) since the last major incident in Sweden. (https://lastnight.in/sweden/)')

