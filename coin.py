import requests
import sopel
from sopel import module
from sopel import formatting

@module.commands('coin')
def coin(bot, trigger):
    name = trigger.group(2)

    response = requests.get(f"https://api.coingecko.com/api/v3/search?query={name}")

    json_response = response.json()

    if len(json_response["coins"]) == 0:
        bot.say("ah ah ah you didn't say the magic word...")
    else:
        response_price = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={json_response['coins'][0]['id']}&vs_currencies=usd")
        data_price = response_price.json()
        price = data_price[json_response['coins'][0]['id']]['usd']

        bot.say(f"{json_response['coins'][0]['name']} ({json_response['coins'][0]['symbol']}) ${price}")