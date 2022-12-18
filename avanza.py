from sopel import module
from sopel import formatting
from bs4 import BeautifulSoup
import requests
import json
import re


@module.commands('aktie', 'a')
def avanzaprices(bot, trigger):
    name = trigger.group(2)

    url = "https://www.avanza.se/ab/component/orderbook_search/?query=<name>"
    url = url.replace("<name>", name)

    response = requests.get(url)

    data = json.loads(response.text)

    id = data[0]["id"]

    url = "https://www.avanza.se/_mobile/market/orderbooklist/<id>"
    url = url.replace("<id>", id)

    response = requests.get(url)

    data = json.loads(response.text)

    stock_name = data[0]["name"]
    last_price = data[0]["lastPrice"]
    currency = data[0]["currency"]
    price_three_months_ago = data[0]["priceThreeMonthsAgo"]
    
    try:
        highest_price = data[0]["highestPrice"]
    except:
        highest_price = "N/A"
        
    try:
        lowest_price = data[0]["lowestPrice"]
    except:
        lowest_price = "N/A"

    change_in_number = data[0]["change"]
    change_in_percent = str(data[0]["changePercent"])
    #change_in_percent = formatting.color(change_in_percent, formatting.colors.RED)

    total_volume_traded = data[0]["totalVolumeTraded"]
    change_in_months = round((float(last_price) - float(price_three_months_ago))/float(price_three_months_ago)*100,1)

    #if int(change_in_months) <= 0:
    #    then:change_in_percent = formatting.color(str(change_in_percent), formatting.colors.RED)
    #elif int(change_in_percent) > 0:
    #    then: change_in_percent = formatting.color(str(change_in_percent), formatting.colors.GREEN)


    #print("Stock: " + str(stock_name) + " " + "Price: " + str(last_price))

    bot.say(f'{stock_name} | {last_price} {currency} | Förändring idag: {change_in_percent} % ({change_in_number} {currency}) | 3 mån: {change_in_months}% ({price_three_months_ago} {currency}) | Volla: {lowest_price} - {highest_price} {currency} | Volym: {total_volume_traded}')
