from sopel import module
from bs4 import BeautifulSoup
import requests
import json
import re


@module.commands('stock')
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
    change_in_percent = data[0]["changePercent"]
    total_volume_traded = data[0]["totalVolumeTraded"]
    change_in_months = round((float(last_price) - float(price_three_months_ago))/float(price_three_months_ago)*100,1)


    #print("Stock: " + str(stock_name) + " " + "Price: " + str(last_price))

    bot.say(f'{stock_name} | {last_price} {currency} | Change: {change_in_percent} % ({change_in_number} {currency}) | 3 m: {change_in_months}% ({price_three_months_ago} {currency}) | Volatility: {lowest_price} - {highest_price} {currency} | Volume: {total_volume_traded}')
