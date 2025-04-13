# Sopel IRC Bot Plugins

A collection of custom plugins for the Sopel IRC bot. These plugins provide various functionalities from financial data to weather information and more.

## Installation

1. Clone this repository to your Sopel modules directory:
```bash
git clone https://github.com/yourusername/sopel-modules.git ~/.sopel/modules/
```

2. Make sure you have the required dependencies installed (see individual plugin sections for specific requirements)

## Available Plugins

### Financial Plugins

- **yf.py** / **yahoofinance.py**: Yahoo Finance integration for stock market data
  - Commands:
    - `.yf <stock symbol>` - Get current stock price and information
    - `.yf <stock symbol> <timeframe>` - Get historical data (e.g., 1d, 5d, 1mo, 1y)
    - `.yf <stock symbol> news` - Get latest news about the stock

- **avanza.py**: Avanza stock market integration
  - Commands:
    - `.a <stock name>` - Get current stock information from Avanza
    - `.a <stock name> <timeframe>` - Get historical data

- **krypto.py**: Cryptocurrency information
  - Commands:
    - `.krypto <coin>` - Get current cryptocurrency price
    - `.krypto <coin> <currency>` - Get price in specific currency

- **coin.py**: Coin-related commands
  - Commands:
    - `.coin <symbol>` - Get current coin price
    - `.coin <symbol> <currency>` - Get price in specific currency

### Weather & Environment

- **pirateweather.py**: Weather information using Pirate Weather API
  - Commands:
    - `.weather <location>` - Get current weather
    - `.forecast <location>` - Get weather forecast

- **pollen.py**: Pollen information
  - Commands:
    - `.pollen <location>` - Get current pollen levels
    - `.pollen forecast <location>` - Get pollen forecast

- **wttr.py**: Weather information using wttr.in
  - Commands:
    - `.wttr <city>` - Get current weather
    - `.wttr <city> <format>` - Get weather in specific format

### Social Media & Content

- **reddit.py**: Reddit integration
  - Commands:
    - `.reddit <subreddit>` - Get top posts from subreddit
    - `.reddit <subreddit> <sort>` - Get posts sorted by (hot, new, top)

- **twitter.py**: Twitter integration
  - Commands:
    - `.twitter <username>` - Get latest tweets
    - `.twitter search <query>` - Search tweets

- **ig.py**: Instagram integration
  - Commands:
    - `.ig <username>` - Get Instagram profile info
    - `.ig <username> recent` - Get recent posts

- **imgur.py**: Imgur integration
  - Commands:
    - `.imgur <query>` - Search Imgur
    - `.imgur random` - Get random image

- **tvmaze.py**: TV show information
  - Commands:
    - `.tv <show name>` - Get show information
    - `.tv schedule` - Get TV schedule

### Swedish-specific

- **biluppgifter.py**: Swedish vehicle information
  - Commands:
    - `.bil <registration number>` - Get vehicle information
    - `.bil <registration number> owner` - Get owner information

- **namnsdag.py**: Swedish name day information
  - Commands:
    - `.namnsdag` - Get today's name day
    - `.namnsdag <date>` - Get name day for specific date

- **svenskel.py**: Swedish language related commands
  - Commands:
    - `.el [snitt|dag|1|2|3|4]` - Get electricity prices
    - `.el forecast` - Get electricity price forecast

- **slangopedia.py**: Swedish slang dictionary
  - Commands:
    - `.slang <word>` - Get slang definition
    - `.slang random` - Get random slang word

### Utility & Fun

- **chatgpt.py**: ChatGPT integration
  - Commands:
    - `.chatgpt <question>` - Ask ChatGPT a question
    - `.chatgpt reset` - Reset conversation

- **chattraknare.py**: Chat statistics
  - Commands:
    - `.stats` - Get chat statistics
    - `.stats <user>` - Get user statistics

- **fredag.py**: Friday-related commands
  - Commands:
    - `.fredag` - Check if it's Friday
    - `.fredag countdown` - Time until next Friday

- **lastnight.py**: Last night information
  - Commands:
    - `.lastnight` - Get latest from lastnight.in/sweden

- **pee.py**: Pee-related commands
  - Commands:
    - `.pee` - Get pee-related information

- **rep.py**: Reputation system
  - Commands:
    - `.rep <user>` - Check user reputation
    - `.rep <user> ++` - Give reputation
    - `.rep <user> --` - Remove reputation

- **subdomain.py**: Subdomain information
  - Commands:
    - `.subdomain <domain>` - Get subdomain information

- **bitte.py**: German language helper
  - Commands:
    - `.bitte <word>` - Get German translation

- **aina.py**: Aina-related commands
  - Commands:
    - `.aina <question>` - Ask Aina a question

## Configuration

Each plugin may require specific configuration in your Sopel config file. Please refer to the individual plugin files for configuration requirements.

## License

This project is licensed under the terms specified in the LICENSE.md file.

## Contributing

Feel free to submit issues and pull requests. All contributions are welcome!

## Support

For support, please open an issue in this repository or contact the maintainer.
