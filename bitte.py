import requests
import sopel
from sopel import module
from sopel import formatting
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


@module.commands('bitte', 'bitcoin')
def bitcoin_price(bot, trigger):
    # create the API URL to fetch the current price of Bitcoin in USD
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

    # make a request to the API to get the current price
    response = requests.get(url)
    data = response.json()
    current_price = data['bitcoin']['usd']

    # get the timeframe from the user
    timeframe = trigger.group(2)

    if not timeframe:
        # If timeframe is not provided, set it to 1d
        timeframe = "1d"
        start_date = datetime.today() - timedelta(days=1)
    else:
        # calculate the start date based on the timeframe
        if timeframe.endswith('d'):
            days = int(timeframe[:-1])
            start_date = datetime.today() - timedelta(days=days)
        elif timeframe.endswith('w'):
            weeks = int(timeframe[:-1])
            start_date = datetime.today() - timedelta(weeks=weeks)
        elif timeframe.endswith('m'):
            months = int(timeframe[:-1])
            start_date = datetime.today().replace(day=1) - timedelta(days=1)
            start_date -= relativedelta(months=months)
        elif timeframe.endswith('y'):
            years = int(timeframe[:-1])
            start_date = datetime.today().replace(day=1, month=1) - timedelta(days=1)
            start_date -= relativedelta(years=years)

    # create the API URL with the start date
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/history?date={start_date.strftime('%d-%m-%Y')}&localization=EN"

    # make a request to the API to get the price from the start date
    response = requests.get(url)
    data = response.json()
    start_price = data['market_data']['current_price']['usd']
    start_price = int(start_price)

    # calculate the percentage difference
    percentage_diff = (current_price - start_price) / start_price * 100

    # format the percentage difference with the color green or red based on whether it's positive or negative
    if percentage_diff < 0:
        percentage_diff = formatting.color(f"{percentage_diff:.2f}%", formatting.colors.RED)
    elif percentage_diff > 0:
        percentage_diff = formatting.color(f"{percentage_diff:.2f}%", formatting.colors.GREEN)

    # format the current price as bold
    current_price = formatting.bold(f"${current_price}")

    # print the results
    bot.say(f"{current_price} ({percentage_diff} - ${start_price} {timeframe} ago)")
