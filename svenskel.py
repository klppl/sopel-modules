from sopel import module
import json
from datetime import date, datetime, timedelta
from statistics import mean
import urllib.request
from functools import lru_cache
from typing import Dict, List, Tuple, Optional

# Cache results with a maximum of 128 entries
@lru_cache(maxsize=128)
def fetch_data(area: str, date_str: str) -> List[Dict]:
    """Fetch electricity price data from Vattenfall API."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0"}
    url = f"https://www.vattenfall.se/api/price/spot/pricearea/{date_str}/{date_str}/{area}"
    
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        raise Exception(f"Failed to fetch data: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response: {str(e)}")

def format_area_data(area: str, area_code: str, date_str: str) -> str:
    """Format electricity price data for a specific area."""
    try:
        data = fetch_data(area_code, date_str)
        if not data:
            return f"No data available for {area} on {date_str}"
            
        values = [(x["Value"], x["TimeStampHour"]) for x in data]
        average = mean([x[0] for x in values])
        max_value, max_timestamp = max(values)
        min_value, min_timestamp = min(values)
        
        return (f'Snittpris {area}: {round(average)} öre/kWh | '
                f'Max: {max_value} öre/kWh - kl {max_timestamp} | '
                f'Lägst: {min_value} öre/kWh - kl {min_timestamp}')
    except Exception as e:
        return f"Error fetching data for {area}: {str(e)}"

def format_daily_prices(data: List[Dict]) -> str:
    """Format daily electricity prices."""
    try:
        output = [f"[{rec['TimeStampHour']} - {rec['Value']}]" 
                 for rec in data 
                 if '06:00' <= rec['TimeStampHour'] <= '23:00']
        return "Elpriser idag SE3 (öre/kWh): " + ' '.join(output)
    except Exception as e:
        return f"Error formatting daily prices: {str(e)}"

@module.commands('el')
def elen(bot, trigger):
    """Get Swedish electricity prices.
    
    Usage:
        .el snitt - Show average prices for all areas
        .el dag - Show daily prices for SE3
        .el [1|2|3|4] - Show detailed prices for specific area
    """
    commando = trigger.group(2)
    if commando is None:
        bot.say("Användning: .el [snitt|dag|1|2|3|4]")
        return

    commando = commando.lower()
    today = date.today().strftime("%Y-%m-%d")
    area_mapping = {"1": "SN1", "2": "SN2", "3": "SN3", "4": "SN4"}

    try:
        if commando == "snitt":
            areas = ["SN1", "SN2", "SN3", "SN4"]
            averages = []
            for area in areas:
                data = fetch_data(area, today)
                values = [x["Value"] for x in data]
                averages.append(mean(values))
            bot.say(f'Snittpris: SE1 {round(averages[0])} öre/kWh | '
                   f'SE2 {round(averages[1])} öre/kWh | '
                   f'SE3 {round(averages[2])} öre/kWh | '
                   f'SE4 {round(averages[3])} öre/kWh')

        elif commando == "dag":
            data = fetch_data("SN3", today)
            bot.say(format_daily_prices(data))

        elif commando in area_mapping:
            area_code = area_mapping[commando]
            area_label = f"SE{commando}"
            bot.say(format_area_data(area_label, area_code, today))

        else:
            bot.say("Användning: .el [snitt|dag|1|2|3|4]")

    except Exception as e:
        bot.say(f"Error: {str(e)}")
