import sopel.module
import requests
import sopel.db
from datetime import datetime
from configparser import ConfigParser
config = ConfigParser()
config.read('/home/pi/keys_config.cfg')
OPENCAGE_API = config.get('pirateweather', 'opencage')
PIRATEWEATHER_API = config.get('pirateweather', 'pirateweather')


def get_weather(lat, lon, api_key):
    base_url = "https://api.pirateweather.net/forecast/"
    full_url = f"{base_url}{api_key}/{lat},{lon}?units=si"
    response = requests.get(full_url)
    return response.json()

def get_emoji(icon):
    icon_dict = {
        "clear-day": "☀️",
        "clear-night": "🌙",
        "rain": "🌧️",
        "snow": "❄️",
        "sleet": "🌨️",
        "wind": "💨",
        "fog": "🌫️",
        "cloudy": "☁️",
        "partly-cloudy-day": "🌤️",
        "partly-cloudy-night": "🌥️"
    }
    return icon_dict.get(icon, "")

def get_uv_index_emoji(uv_index):
    if uv_index <= 2:
        return "🟢"  
    elif 3 <= uv_index <= 5:
        return "🟡"  
    elif 6 <= uv_index <= 7:
        return "🟠"  
    elif 8 <= uv_index <= 10:
        return "🔴"  
    else:
        return "🟣"  

def print_weather(weather):
    current_weather = weather['currently']
    daily_data = weather['daily']['data'][0]
    weather_emoji = get_emoji(current_weather.get('icon', ''))
    humidity = current_weather['humidity'] * 100
    temp_max = daily_data.get('temperatureMax', 'N/A')
    temp_min = daily_data.get('temperatureMin', 'N/A')
    uv_index = daily_data.get('uvIndex', 'No data')
    uv_index_emoji = get_uv_index_emoji(uv_index)
    uv_index_time = datetime.fromtimestamp(daily_data.get('uvIndexTime')).strftime('%H:%M') if 'uvIndexTime' in daily_data else 'No data'
    return f"{weather_emoji} {current_weather['summary']}, Temp: {round(current_weather['temperature'])}°C (H: {round(temp_max)}°C L: {round(temp_min)}°C), Luftfuktighet: {humidity}%, UV: {uv_index_emoji} {current_weather['uvIndex']}, Soluppgång: {datetime.fromtimestamp(daily_data['sunriseTime']).strftime('%H:%M')}, Solnedgång: {datetime.fromtimestamp(daily_data['sunsetTime']).strftime('%H:%M')}"

def get_coordinates(city, opencage_api_key):
    opencage_url = f'https://api.opencagedata.com/geocode/v1/json?q={city}&key={opencage_api_key}'
    response = requests.get(opencage_url)
    data = response.json()
    if 'results' in data and len(data['results']) > 0:
        return data['results'][0]['geometry']['lat'], data['results'][0]['geometry']['lng']
    else:
        return None, None

@sopel.module.commands("weather", "vädret", "väder", "v")
def weather(bot, trigger):
    pirateweather_api_key = PIRATEWEATHER_API
    opencage_api_key = OPENCAGE_API
    city = trigger.group(2)
    if not city:
        city = bot.db.get_nick_value(trigger.nick, 'location')
        if not city:
            bot.say("Du glömde nått .vädret Stockholm")
            return
    lat, lon = get_coordinates(city, opencage_api_key)
    if lat is not None and lon is not None:
        weather = get_weather(lat, lon, pirateweather_api_key)
        bot.say(print_weather(weather))
    else:
        bot.say("Hittar inte plejset, sorry!")

@sopel.module.commands("väderplats")
def set_location(bot, trigger):
    city = trigger.group(2)
    if not city:
        bot.say("Ange plejs, exempel .väderplats Stockholm")
        return
    bot.db.set_nick_value(trigger.nick, 'location', city)
    bot.say(f"Sparat {trigger.nick}s plejs till {city}")

