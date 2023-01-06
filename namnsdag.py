import sopel
import requests
from bs4 import BeautifulSoup

@sopel.module.commands('namnsdag')
def namnsdag(bot, trigger):
    # Fetch the name of the current name day from the web
    r = requests.get('https://www.dagensnamn.nu/')
    soup = BeautifulSoup(r.text, 'html.parser')
    name = soup.find('h1').text.strip()

    # Reply with the name
    bot.say(f'Namnsdag idag {name}')
