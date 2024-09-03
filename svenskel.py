from sopel import module
import json
from datetime import date
from statistics import mean
import urllib.request

@module.commands('el')
def elen(bot, trigger):
    commando = trigger.group(2)
    if commando is None:
        bot.say("Användning: .el [snitt|dag|1|2|3|4]")
        return

    commando = commando.lower()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0"}
    today = date.today().strftime("%Y-%m-%d")

    def fetch_data(area):
        url = f"https://www.vattenfall.se/api/price/spot/pricearea/{today}/{today}/{area}"
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as response:
            return json.loads(response.read().decode())

    def format_area_data(area, area_code):
        data = fetch_data(area_code)
        values = [(x["Value"], x["TimeStampHour"]) for x in data]
        average = mean([x[0] for x in values])
        max_value, max_timestamp = max(values)
        min_value, min_timestamp = min(values)
        return f'Snittpris {area}: {round(average)} öre/kWh | Max: {max_value} öre/kWh - kl {max_timestamp} | Lägst: {min_value} öre/kWh - kl {min_timestamp}'

    if commando == "snitt":
        areas = ["SN1", "SN2", "SN3", "SN4"]
        averages = []
        for area in areas:
            data = fetch_data(area)
            values = [x["Value"] for x in data]
            averages.append(mean(values))
        bot.say(f'Snittpris: SE1 {round(averages[0])} öre/kWh | SE2 {round(averages[1])} öre/kWh | SE3 {round(averages[2])} öre/kWh | SE4 {round(averages[3])} öre/kWh')

    elif commando == "dag":
        data = fetch_data("SN3")
        output = [f"[{rec['TimeStampHour']} - {rec['Value']}]" for rec in data if '06:00' <= rec['TimeStampHour'] <= '23:00']
        bot.say("Elpriser idag SE3 (öre/kWh): " + ' '.join(output))

    elif commando in ["1", "2", "3", "4"]:
        area_mapping = {"1": "SN1", "2": "SN2", "3": "SN3", "4": "SN4"}
        area_code = area_mapping[commando]
        area_label = f"SE{commando}"
        bot.say(format_area_data(area_label, area_code))

    else:
        bot.say("Användning: .el [snitt|dag|1|2|3|4]")
