from sopel import module
import requests

@module.commands('pollen')
def pollen(bot, trigger):
    region_name = trigger.group(2)

    if region_name:
        forecast = get_forecast(region_name)
        bot.say(forecast)
    else:
        bot.say("Var ska jag kolla?")

def get_forecast(region_name):
    regions_url = "https://api.pollenrapporten.se/v1/regions"

    try:
        response = requests.get(regions_url)
        response.raise_for_status()

        data = response.json()

        forecasts_url = None
        for item in data["items"]:
            if item["name"].lower() == region_name.lower():
                forecasts_url = item["forecasts"]
                break

        if forecasts_url:
            forecasts_response = requests.get(forecasts_url)
            forecasts_response.raise_for_status()

            forecasts_data = forecasts_response.json()

            forecast_text = forecasts_data["items"][0]["text"]
            return "{}: {}".format(region_name, forecast_text)
        else:
            region_names = [item["name"] for item in data["items"]]
            if region_name.lower() not in [name.lower() for name in region_names]:
                return "Hittar ingen prognos. Kör någon av följande: {}".format(", ".join(region_names))
            else:
                return "{}: Hittar ingen prognos.".format(region_name)

    except requests.exceptions.RequestException as e:
        return "Något gick fel: {}".format(e)
