from sopel import module
from sopel.config.types import StaticSection, ValidatedAttribute
from datetime import datetime
import requests
import re

@module.commands('vädret')
def vadret(bot, trigger):
    city = trigger.group(2)

    trigger = re.sub('(<.*?>) ?', '', trigger)
    trigger = re.sub(r'\..\S*(\s)?', '', trigger)

    if (not trigger):
        bot.say('vadret <ort>')
        return
    else:
        city = trigger.strip()

    api_key = "e92ab480689e82d5fb1c1d0488f598ef"
    apiurl = 'http://api.openweathermap.org/data/2.5/weather?units=metric&appid=' + api_key

    iconos = {
        '01d' : '☀️',
        '01n' : '🌙',
        '02d' : '🌥',
        '02n' : '🌥',
        '03d' : '☁️',
        '03n' : '☁️',
        '04d' : '☁️',
        '04n' : '☁️',
        '09d' : '🌦',
        '09n' : '🌦',
        '10d' : '🌧',
        '10n' : '🌧',
        '11d' : '⛈',
        '11n' : '⛈',
        '13d' : '🌨',
        '13n' : '🌨',
        '50d' : '🌫',
        '50n' : '🌫'
    }

    #apiurl = apiurl + '&q=' + city + ',ar' 
    apiurlarg = apiurl + '&q=' + city + ',ar'
    apiurl = apiurl + '&q=' + city

    try:
        r = requests.get(apiurlarg)
    except:
        raise Exception("¯\_(ツ)_/¯")

    data = r.json()
    if r.status_code != 200:
        try:
            r = requests.get(apiurl)
        except:
            raise Exception("¯\_(ツ)_/¯")
        data = r.json()
        if r.status_code != 200:
            raise Exception('¯\_(ツ)_/¯: {}'.format(data['message']))
        else:
            timezone = int(data['timezone'])
            sunset_utc = int(data['sys']['sunset'])
            sunset_local = datetime.utcfromtimestamp(sunset_utc + timezone).strftime('%H:%M')
            #print('sunset : {}'.format(sunset_local))

            vadret = f"{iconos[data['weather'][0]['icon']]} - {data['name']}, {data['sys']['country']}: {round(data['main']['temp'])}˚C - min: {round(data['main']['temp_min'])}˚C, max: {round(data['main']['temp_max'])}˚C - Luftfuktighet {data['main']['humidity']}% - Känns som {round(data['main']['feels_like'])}˚C - Solnedgång: {sunset_local}"
            bot.say(vadret)
    else:
        vadret = f"{iconos[data['weather'][0]['icon']]} - {data['name']}, {data['sys']['country']}: {data['main']['temp']}˚C - min: {data['main']['temp_min']}˚C, max: {data['main']['temp_max']}˚C - Luftfuktighet {data['main']['humidity']}%. - Känns som {data['main']['feels_like']}˚C"
        bot.say(vadret)

