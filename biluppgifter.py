import sopel.module
from sopel.config.types import StaticSection, ValidatedAttribute
import requests
from bs4 import BeautifulSoup
import re

TAG_RE = re.compile(r'<[^>]+>')


class VehicleInfoSection(StaticSection):
    token = ValidatedAttribute('token')


def configure(config):
    config.define_section('vehicle_info', VehicleInfoSection, validate=False)
    config.vehicle_info.configure_setting('token', 'Enter your Discord token:')


def setup(bot):
    bot.config.define_section('vehicle_info', VehicleInfoSection)


def removeHTML(text):
    return TAG_RE.sub('', text)


def GetInfoAbout(reg):
    try:
        URL = 'https://biluppgifter.se/fordon/' + reg
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        ownerLink = soup.findAll("a", {"class": "gtm-merinfo"})
        OwnerLink = str(ownerLink)
        fabikat = soup.findAll("h1", {"class": "card-title"})
        fabrikat = str(fabikat)
        Fabrikat = removeHTML(fabrikat)
        Fabrikat1 = "".join(Fabrikat.splitlines())
        Fabrikat2 = Fabrikat1.replace('[', '')
        FabrikatOrig = Fabrikat2.replace(']', '')

        description = soup.findAll("img", {"src": "/images/maker/"})
        print(description)

        OwnerLink = "".join(OwnerLink.splitlines())

        OwnerLink1 = OwnerLink.replace("[<a class=\"gtm-merinfo\" href=\"", '')
        OwnerLink2 = OwnerLink1.replace("\" rel=\"follow\" target=\"_blank\">Visa kompletta ägaruppgifter på Merinfo.se</a>]", '')

        return ("Regnummer: " + reg + " | " +
                "Fabrikat: " + FabrikatOrig + " | " +
                "Ägare: " + OwnerLink2 + " | " +
                "Länk till bil: " + "https://biluppgifter.se/fordon/" + reg.upper())

    except Exception as e:
        return e



@sopel.module.commands('bil')
def regnr(bot, trigger):
    regnr = trigger.group(2).upper()
    bot.say(GetInfoAbout(regnr))
