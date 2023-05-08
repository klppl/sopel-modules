import re
import requests
from bs4 import BeautifulSoup
import sopel.module

TAG_RE = re.compile(r'<[^>]+>')

def remove_html_tags(text):
    return TAG_RE.sub('', text)

def get_vehicle_info(reg):
    try:
        url = f'https://biluppgifter.se/fordon/{reg}'
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        owner_link = soup.findAll("a", {"class": "gtm-merinfo"})
        owner_link = str(owner_link)
        fabrikat = soup.findAll("h1", {"class": "card-title"})
        fabrikat = str(fabrikat)
        fabrikat = remove_html_tags(fabrikat).strip('[]')

        owner_link = owner_link.replace("[<a class=\"gtm-merinfo\" href=\"", '')
        owner_link = owner_link.replace("\" rel=\"follow\" target=\"_blank\">Visa kompletta ägaruppgifter på Merinfo.se</a>]", '')

        return f"Regnummer: {reg} | Fabrikat: {fabrikat} | Ägare: {owner_link} | Länk till bil: https://biluppgifter.se/fordon/{reg.upper()}"

    except Exception as e:
        return e

@sopel.module.commands('bil')
def regnr(bot, trigger):
    regnr = trigger.group(2).upper()
    bot.say(get_vehicle_info(regnr))
