import sopel.module
import requests
from configparser import ConfigParser
config = ConfigParser()
config.read('/home/pi/keys_config.cfg')
OPENCAGE_API_KEY = config.get('weather', 'opencage')
TOMORROW_API_KEY = config.get('weather', 'tomorrow')

@sopel.module.commands('vädret')
def weather(bot, trigger):
    city = trigger.group(2)
    lat, lon = get_coordinates(city)
    if lat is not None and lon is not None:
        temperature, cloud_cover, wind_speed, humidity, uv_index, weather_code = get_weather(lat, lon)
        weather_code_data = get_weather_code_description(weather_code)
        if temperature is not None and cloud_cover is not None and wind_speed is not None and humidity is not None and uv_index is not None and weather_code is not None:
            bot.say(f'{weather_code_data["emoji"]} {weather_code_data["description"]} Temp: {temperature}°C Moln: {cloud_cover}% Vind: {wind_speed} m/s Luftfuktighet: {humidity}% UV: {uv_index} {get_uv_index_emoji(uv_index)}')
        else:
            bot.say('Hittar inte väderdata.')
    else:
        bot.say('Hittar inte koordinater.')

def get_coordinates(city):
    opencage_api_key = OPENCAGE_API_KEY
    opencage_url = f'https://api.opencagedata.com/geocode/v1/json?q={city}&key={opencage_api_key}'
    response = requests.get(opencage_url)
    data = response.json()
    if 'results' in data and len(data['results']) > 0:
        return data['results'][0]['geometry']['lat'], data['results'][0]['geometry']['lng']
    else:
        return None, None

def get_weather(lat, lon):
    tomorrow_io_api_key = TOMORROW_API_KEY
    tomorrow_io_url = f"https://api.tomorrow.io/v4/weather/realtime?location={lat},{lon}&apikey={tomorrow_io_api_key}"
    headers = {"accept": "application/json"}
    response = requests.get(tomorrow_io_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'values' in data['data']:
            temperature = int(data['data']['values'].get('temperature'))
            cloud_cover = data['data']['values'].get('cloudCover')
            wind_speed = data['data']['values'].get('windSpeed')
            humidity = data['data']['values'].get('humidity')
            uv_index = data['data']['values'].get('uvIndex')
            weather_code = data['data']['values'].get('weatherCode')
            return temperature, cloud_cover, wind_speed, humidity, uv_index, weather_code
    return None, None, None, None, None, None

def get_weather_code_description(weather_code):
    weather_codes = {
        "0": {"description": "Okänt", "emoji": "❔"},
        "1000": {"description": "Klart, soligt", "emoji": "☀️"},
        "1100": {"description": "Mestadels klart", "emoji": "🌤"},
        "1101": {"description": "Delvis molnigt", "emoji": "⛅"},
        "1102": {"description": "Mestadels molnigt", "emoji": "🌥"},
        "1001": {"description": "Molnigt", "emoji": "☁️"},
        "2000": {"description": "Dimma", "emoji": "🌫"},
        "2100": {"description": "Lätt dimma", "emoji": "🌁"},
        "4000": {"description": "Duggregn", "emoji": "🌧"},
        "4001": {"description": "Regn", "emoji": "🌧"},
        "4200": {"description": "Lätt regn", "emoji": "🌦"},
        "4201": {"description": "Kraftigt regn", "emoji": "🌧"},
        "5000": {"description": "Snö", "emoji": "❄️"},
        "5001": {"description": "Snöblandat regn", "emoji": "🌨"},
        "5100": {"description": "Lätt snöfall", "emoji": "🌨"},
        "5101": {"description": "Kraftigt snöfall", "emoji": "❄️"},
        "6000": {"description": "Underkylt duggregn", "emoji": "🌧"},
        "6001": {"description": "Underkylt regn", "emoji": "🌧"},
        "6200": {"description": "Lätt underkylt regn", "emoji": "🌧"},
        "6201": {"description": "Kraftigt underkylt regn", "emoji": "🌧"},
        "7000": {"description": "Hagel", "emoji": "🌨"},
        "7101": {"description": "Kraftigt hagel", "emoji": "🌨"},
        "7102": {"description": "Lätt hagel", "emoji": "🌨"},
        "8000": {"description": "Åskväder", "emoji": "🌩"}
    }

    
    return weather_codes.get(str(weather_code), {"description": "Unknown", "emoji": "❔"})

def get_uv_index_emoji(uv_index):
    if uv_index is None:
        return ''
    elif uv_index <= 2:
        return '🟢'
    elif uv_index <= 5:
        return '🟡'
    elif uv_index <= 7:
        return '🟠'
    elif uv_index <= 10:
        return '🔴'
    else:
        return '🟣'

