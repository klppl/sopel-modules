from sopel import module
from sopel import formatting
import requests
import json
import sqlite3
import os

def get_stock_from_db(stock_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "avanza_data.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = """
        SELECT id, name, currency FROM orderbooklist 
        WHERE instrumentType = 'STOCK' AND name LIKE ? COLLATE NOCASE
    """
    cursor.execute(query, ('%' + stock_name + '%',))
    row = cursor.fetchone()
    conn.close()
    return row

@module.commands('aktie', 'a')
def avanzaprices(bot, trigger):
    stock_query = trigger.group(2)
    if not stock_query:
        bot.say("Ange ett aktienamn!")
        return

    stock = get_stock_from_db(stock_query)
    if not stock:
        bot.say("Hittade inget!")
        return
    stock_id, stock_name, stock_currency = stock

    try:
        url = "https://www.avanza.se/_mobile/market/orderbooklist/" + stock_id
        data = json.loads(requests.get(url, timeout=10).text)
    except Exception:
        bot.say("Fel vid hämtning av data.")
        return

    try:
        stock_data = data[0]
    except (IndexError, TypeError):
        bot.say("Hittade inget data för aktien.")
        return

    stock_name = stock_data.get("name", stock_name)
    last_price = stock_data.get("lastPrice", "N/A")
    currency = stock_data.get("currency", stock_currency)
    price_three_months_ago = stock_data.get("priceThreeMonthsAgo", "N/A")
    lowest_price = stock_data.get("lowestPrice", "N/A")
    highest_price = stock_data.get("highestPrice", "N/A")
    change_in_number = stock_data.get("change", "N/A")
    change_in_percent = stock_data.get("changePercent", "N/A")

    try:
        if float(change_in_percent) < 0:
            change_in_percent = formatting.color(str(change_in_percent) + '%', formatting.colors.RED)
        elif float(change_in_percent) > 0:
            change_in_percent = formatting.color(str(change_in_percent) + '%', formatting.colors.GREEN)
        else:
            change_in_percent = str(change_in_percent) + '%'
    except (ValueError, TypeError):
        change_in_percent = str(change_in_percent) + '%'

    try:
        change_in_months = round((float(last_price) - float(price_three_months_ago)) / float(price_three_months_ago) * 100, 1)
    except Exception:
        change_in_months = "N/A"

    try:
        if isinstance(change_in_months, (int, float)) and change_in_months < 0:
            change_in_months = formatting.color(str(change_in_months) + '%', formatting.colors.RED)
        elif isinstance(change_in_months, (int, float)) and change_in_months > 0:
            change_in_months = formatting.color(str(change_in_months) + '%', formatting.colors.GREEN)
        else:
            change_in_months = str(change_in_months) + '%'
    except Exception:
        change_in_months = str(change_in_months) + '%'

    bot.say(f'{stock_name} | {last_price} {currency} | Idag: {change_in_percent} ({change_in_number} {currency}) | '
            f'3 mån: {change_in_months} ({price_three_months_ago} {currency}) | '
            f'Volla: {lowest_price} - {highest_price} {currency} | Volym: {stock_data.get("totalVolumeTraded", "N/A")}')

@module.commands('afind', 'af')
def avanzafind(bot, trigger):
    stock_name = trigger.group(2)
    url = f"https://www.avanza.se/_cqbe/search/global-search/global-search-template?query={stock_name}"
    response = requests.get(url)
    data = json.loads(response.content)
    link_displays = []
    for result_group in data.get("resultGroups", []):
        for hit in result_group.get("hits", []):
            link_displays.append(hit["link"]["linkDisplay"])
    bot.say(", ".join(link_displays))

@module.commands('index', 'i')
def avanzaindex(bot, trigger):
    indices = {
        "OMXS30": "19002",
        "NASDAQ": "19006",
        "DAX": "18981",
        "Nikkei225": "18997"
    }
    for index_name, index_id in indices.items():
        try:
            data = json.loads(requests.get("https://www.avanza.se/_mobile/market/orderbooklist/" + index_id, timeout=10).text)
            stock_data = data[0]
        except Exception:
            bot.say(f"Kunde inte hämta data för {index_name}")
            continue

        stock_name = stock_data.get("name", "N/A")
        last_price = stock_data.get("lastPrice", "N/A")
        currency = stock_data.get("currency", "N/A")
        price_three_months_ago = stock_data.get("priceThreeMonthsAgo", "N/A")
        lowest_price = stock_data.get("lowestPrice", "N/A")
        highest_price = stock_data.get("highestPrice", "N/A")
        change_in_number = stock_data.get("change", "N/A")
        change_in_percent = stock_data.get("changePercent", "N/A")
        try:
            if float(change_in_percent) < 0:
                change_in_percent = formatting.color(str(change_in_percent) + '%', formatting.colors.RED)
            elif float(change_in_percent) > 0:
                change_in_percent = formatting.color(str(change_in_percent) + '%', formatting.colors.GREEN)
            else:
                change_in_percent = str(change_in_percent) + '%'
        except Exception:
            change_in_percent = str(change_in_percent) + '%'

        try:
            change_in_months = round((float(last_price) - float(price_three_months_ago)) / float(price_three_months_ago) * 100, 1)
        except Exception:
            change_in_months = "N/A"
        try:
            if isinstance(change_in_months, (int, float)) and change_in_months < 0:
                change_in_months = formatting.color(str(change_in_months) + '%', formatting.colors.RED)
            elif isinstance(change_in_months, (int, float)) and change_in_months > 0:
                change_in_months = formatting.color(str(change_in_months) + '%', formatting.colors.GREEN)
            else:
                change_in_months = str(change_in_months) + '%'
        except Exception:
            change_in_months = str(change_in_months) + '%'

        total_volume_traded = stock_data.get("totalVolumeTraded", "N/A")
        bot.say(f'{stock_name} | {last_price} {currency} | Idag: {change_in_percent} ({change_in_number} {currency}) | '
                f'3 mån: {change_in_months} ({price_three_months_ago} {currency}) | '
                f'Volla: {lowest_price} - {highest_price} {currency} | Volym: {total_volume_traded}')
