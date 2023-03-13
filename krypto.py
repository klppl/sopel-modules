import requests
import sopel
from sopel import module
from sopel import formatting

@module.commands('krypto')
def crypto(bot, trigger):
    """Replies with the current price of bitcoin and ethereum."""
    # Get the latest prices from coingecko API
    response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin%2Cethereum%2Cusd-coin%2Ccardano%2Cdogecoin%2Cpolkadot%2Cmonero&vs_currencies=usd')
    data = response.json()
    # Format the output message
    btc_price = data['bitcoin']['usd']
    eth_price = data['ethereum']['usd']
    usdc_price = data['usd-coin']['usd']
    cardano_price = data['cardano']['usd']
    dogecoin_price = data['dogecoin']['usd']
    polkadot_price = data['polkadot']['usd']
    monero_price = data['monero']['usd']

    message = f'BTC: ${btc_price:.2f} ETH: ${eth_price:.2f} USDC: ${usdc_price:.2f} ADA: ${cardano_price:.2f} DOGE: ${dogecoin_price:.2f} DOT: ${polkadot_price:.2f} XMR: ${monero_price:.2f}'
    # Send the message to the channel
    bot.say(message)


