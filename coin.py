import requests
import sopel
from sopel import module
from sopel import formatting

@module.commands('coin')
def coin(bot, trigger):
    coins = trigger.group(2)
    if coins:
        coin_list = coins.split(",")
        result = []
        for name in coin_list:
            response = requests.get(f"https://api.coingecko.com/api/v3/search?query={name.strip()}")
            json_response = response.json()

            if len(json_response["coins"]) == 0:
                result.append(f"(404 {name.strip()})")
            else:
                response_price = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={json_response['coins'][0]['id']}&vs_currencies=usd")
                data_price = response_price.json()

                symbol = formatting.bold(json_response['coins'][0]['symbol'])
                price = data_price[json_response['coins'][0]['id']]['usd']
                result.append(f"{symbol} {price}")

        bot.say("$ " + " ".join(result))
    else:
        bot.say(".coin crypto or .coin crypto,separated,with,commas")
