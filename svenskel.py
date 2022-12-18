from sopel import module
import json
from datetime import date
from datetime import datetime
from statistics import mean
import urllib.request
import requests

@module.commands('el')
def elen(bot, trigger):
    commando = trigger.group(2)
    if commando == None:
        bot.say("Användning: .el [snitt|dag|1|2|3|4]")
        return
    else:
        commando = commando.lower()

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0"}
    today = date.today().strftime("%Y-%m-%d")
    
    if commando == "snitt":

        with urllib.request.urlopen(urllib.request.Request(f"https://www.vattenfall.se/api/price/spot/pricearea/{today}/{today}/SN1", headers=headers)) as url:
            data = json.loads(url.read().decode())

        values = [x["Value"] for x in data]
        average1 = mean(values)

        with urllib.request.urlopen(urllib.request.Request(f"https://www.vattenfall.se/api/price/spot/pricearea/{today}/{today}/SN2", headers=headers)) as url:
            data = json.loads(url.read().decode())

        values = [x["Value"] for x in data]
        average2 = mean(values)

        with urllib.request.urlopen(urllib.request.Request(f"https://www.vattenfall.se/api/price/spot/pricearea/{today}/{today}/SN3", headers=headers)) as url:
            data = json.loads(url.read().decode())

        values = [x["Value"] for x in data]
        average3 = mean(values)

        with urllib.request.urlopen(urllib.request.Request(f"https://www.vattenfall.se/api/price/spot/pricearea/{today}/{today}/SN4", headers=headers)) as url:
            data = json.loads(url.read().decode())

        values = [x["Value"] for x in data]
        average4 = mean(values)

        bot.say(f'Snittpris: SE1 {round(average1)} öre/kWh | SE2 {round(average2)} öre/kWh | SE3 {round(average3)} öre/kWh | SE4 {round(average4)} öre/kWh')

    elif commando == "dag":

        url = f"https://www.vattenfall.se/api/price/spot/pricearea/{today}/{today}/SN3"

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

        output = []

        for record in data:
            if record['TimeStampHour'] >= '06:00' and record['TimeStampHour'] <= '23:00':
                output.append(f"[{record['TimeStampHour']} - {record['Value']}]")

        output_string = ' '.join(output)

        bot.say("Elpriser idag SE3 (öre/kWh): " + output_string)
    
    elif commando == "1":

        with urllib.request.urlopen(urllib.request.Request(f"https://www.vattenfall.se/api/price/spot/pricearea/{today}/{today}/SN1", headers=headers)) as url:
            data = json.loads(url.read().decode())

        values = [(x["Value"], x["TimeStampHour"]) for x in data]
        average1 = mean([x[0] for x in values])
        max_value, max_timestamp = max(values)
        min_value, min_timestamp = min(values)

        bot.say(f'Snittpris SE1: {round(average1)} öre/kWh | Max: {max_value} öre/kWh - kl {max_timestamp} | Lägst: {min_value} öre/kWh - kl {min_timestamp}')
    elif commando == "2":

        with urllib.request.urlopen(urllib.request.Request(f"https://www.vattenfall.se/api/price/spot/pricearea/{today}/{today}/SN2", headers=headers)) as url:
            data = json.loads(url.read().decode())

        values = [(x["Value"], x["TimeStampHour"]) for x in data]
        average2 = mean([x[0] for x in values])
        max_value, max_timestamp = max(values)
        min_value, min_timestamp = min(values)

        bot.say(f'Snittpris SE2: {round(average2)} öre/kWh | Max: {max_value} öre/kWh - kl {max_timestamp} | Lägst: {min_value} öre/kWh - kl {min_timestamp}')
    elif commando == "3":

        with urllib.request.urlopen(urllib.request.Request(f"https://www.vattenfall.se/api/price/spot/pricearea/{today}/{today}/SN3", headers=headers)) as url:
            data = json.loads(url.read().decode())

        values = [(x["Value"], x["TimeStampHour"]) for x in data]
        average3 = mean([x[0] for x in values])
        max_value, max_timestamp = max(values)
        min_value, min_timestamp = min(values)

        bot.say(f'Snittpris SE3: {round(average3)} öre/kWh | Max: {max_value} öre/kWh - kl {max_timestamp} | Lägst: {min_value} öre/kWh - kl {min_timestamp}')
    elif commando == "4":

        with urllib.request.urlopen(urllib.request.Request(f"https://www.vattenfall.se/api/price/spot/pricearea/{today}/{today}/SN4", headers=headers)) as url:
            data = json.loads(url.read().decode())

        values = [(x["Value"], x["TimeStampHour"]) for x in data]
        average4 = mean([x[0] for x in values])
        max_value, max_timestamp = max(values)
        min_value, min_timestamp = min(values)

        bot.say(f'Snittpris SE4: {round(average4)} öre/kWh | Max: {max_value} öre/kWh - kl {max_timestamp} | Lägst: {min_value} öre/kWh - kl {min_timestamp}')
    else:
        bot.say("Användning: .el [snitt|dag|1|2|3|4]")