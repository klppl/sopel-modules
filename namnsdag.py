import sopel
import requests
from bs4 import BeautifulSoup

@sopel.module.commands('namnsdag')
@sopel.module.rate(30)  # Limit to once every 30 seconds
def namnsdag(bot, trigger):
    """Shows today's name day (namnsdag) in Sweden."""
    try:
        # Fetch the name of the current name day from the web
        r = requests.get('https://www.dagensnamn.nu/', timeout=10)
        r.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(r.text, 'html.parser')
        name = soup.find('h1').text.strip()
        
        # Reply with the name
        bot.say(f'Namnsdag idag {name}')
        
    except requests.exceptions.RequestException as e:
        bot.say('Kunde inte hämta namnsdagen just nu. Försök igen senare.')
        bot.say(f'Fel: {str(e)}')
    except Exception as e:
        bot.say('Ett oväntat fel uppstod när namnsdagen skulle hämtas.')
        bot.say(f'Fel: {str(e)}')
