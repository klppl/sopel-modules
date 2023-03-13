from sopel import module
from sopel import formatting
from bs4 import BeautifulSoup
import requests
import json
import re


@module.commands('aktie', 'a')
def avanzaprices(bot, trigger):

    try:
        find_stock = json.loads(requests.get("https://www.avanza.se/ab/component/orderbook_search/?query=" + trigger.group(2)).text)
        id = find_stock[0]["id"]
    except IndexError:
        bot.say("Hittade inget!")
        return

    data = json.loads(requests.get("https://www.avanza.se/_mobile/market/orderbooklist/" + id).text)

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
    if int(change_in_percent) <0:
        change_in_percent = formatting.color(str(change_in_percent) + '%', formatting.colors.RED)
    elif change_in_percent >0:
        change_in_percent = formatting.color(str(change_in_percent) + '%', formatting.colors.GREEN)

    change_in_months = round((float(last_price) - float(price_three_months_ago))/float(price_three_months_ago)*100,1)
    if int(change_in_months) <0:
        change_in_months = formatting.color(str(change_in_months) + '%', formatting.colors.RED)
    elif change_in_months >0:
        change_in_months = formatting.color(str(change_in_months) + '%', formatting.colors.GREEN)

    total_volume_traded = data[0]["totalVolumeTraded"]

    bot.say(f'{stock_name} | {last_price} {currency} | Idag: {change_in_percent} ({change_in_number} {currency}) | 3 mån: {change_in_months} ({price_three_months_ago} {currency}) | Volla: {lowest_price} - {highest_price} {currency} | Volym: {total_volume_traded}')


@module.commands('afind', 'af')
def avanzafind(bot, trigger):

    # Get user input
    stock_name = trigger.group(2)

    # Create URL with user input
    url = f"https://www.avanza.se/_cqbe/search/global-search/global-search-template?query={stock_name}"

    # Get JSON data from URL
    response = requests.get(url)
    data = json.loads(response.content)

    link_displays = []
    for result_group in data["resultGroups"]:
        for hit in result_group["hits"]:
            link_displays.append(hit["link"]["linkDisplay"])
    
    bot.say(", ".join(link_displays))

@module.commands('index', 'i')
def avanzaindex(bot, trigger):

    omxs30 = "19002"
    nasdaq = "19006"
    dax = "18981"
    nikkei225 = "18997"
    index_list = [omxs30, nasdaq, dax, nikkei225]

    for index in index_list:
        data = json.loads(requests.get("https://www.avanza.se/_mobile/market/orderbooklist/" + index).text

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
        if int(change_in_percent) <0:
            change_in_percent = formatting.color(str(change_in_percent) + '%', formatting.colors.RED)
        elif change_in_percent >0:
            change_in_percent = formatting.color(str(change_in_percent) + '%', formatting.colors.GREEN)

        change_in_months = round((float(last_price) - float(price_three_months_ago))/float(price_three_months_ago)*100,1)
        if int(change_in_months) <0:
            change_in_months = formatting.color(str(change_in_months) + '%', formatting.colors.RED)
        elif change_in_months >0:
            change_in_months = formatting.color(str(change_in_months) + '%', formatting.colors.GREEN)

        total_volume_traded = data[0]["totalVolumeTraded"]
        
        bot.say(f'{stock_name} | {last_price} {currency} | Idag: {change_in_percent} ({change_in_number} {currency}) | 3 mån: {change_in_months} ({price_three_months_ago} {currency}) | Volla: {lowest_price} - {highest_price} {currency} | Volym: {total_volume_traded}')

