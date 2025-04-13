# Sopel IRC Bot Plugins

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)
[![Python](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)
[![Sopel](https://img.shields.io/badge/sopel-7.0%2B-green)](https://sopel.chat)

A collection of custom plugins for the Sopel IRC bot. These plugins provide various functionalities from financial data to weather information and more.

## Requirements

- Python 3.6 or higher
- Sopel 7.0 or higher
- pip (Python package installer)

## Installation

1. Clone this repository to your Sopel modules directory:
```bash
git clone https://github.com/yourusername/sopel-modules.git ~/.sopel/modules/
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys in your Sopel configuration file (~/.sopel/default.cfg):
```ini
[pirateweather]
api_key = your_api_key_here

[chatgpt]
api_key = your_openai_api_key_here

[yahoofinance]
api_key = your_api_key_here

# Add other API keys as needed
```

## Available Plugins

### Financial Data
| Plugin | Description | Dependencies | API Key Required |
|--------|-------------|--------------|------------------|
| yf.py / yahoofinance.py | Yahoo Finance integration | yfinance | Yes |
| avanza.py | Avanza market data | avanza-api | No |
| krypto.py | Cryptocurrency info | requests | No |
| coin.py | Coin price tracking | requests | No |

### Weather & Environment
| Plugin | Description | Dependencies | API Key Required |
|--------|-------------|--------------|------------------|
| pirateweather.py | Weather information | requests | Yes |
| pollen.py | Pollen information | requests | No |
| wttr.py | Weather via wttr.in | requests | No |

### Social Media & Content
| Plugin | Description | Dependencies | API Key Required |
|--------|-------------|--------------|------------------|
| reddit.py | Reddit integration | praw | Yes |
| twitter.py | Twitter integration | tweepy | Yes |
| ig.py | Instagram integration | instaloader | No |
| imgur.py | Imgur integration | imgurpython | Yes |
| tvmaze.py | TV show information | requests | No |

### Swedish Services
| Plugin | Description | Dependencies | API Key Required |
|--------|-------------|--------------|------------------|
| biluppgifter.py | Vehicle information | requests | No |
| namnsdag.py | Name day information | requests | No |
| svenskel.py | Electricity prices | requests | No |
| slangopedia.py | Slang dictionary | requests | No |
| fredag.py | Friday checker | None | No |

### Utility & Fun
| Plugin | Description | Dependencies | API Key Required |
|--------|-------------|--------------|------------------|
| chatgpt.py | ChatGPT integration | openai | Yes |
| chattraknare.py | Chat statistics | sqlite3 | No |
| rep.py | Reputation system | sqlite3 | No |
| subdomain.py | Domain information | dns.resolver | No |
| bitte.py | German translations | requests | No |
| aina.py | Q&A bot | None | No |
| pee.py | Pee information | None | No |

## Plugin Usage

### fredag.py
Responds to questions about whether it's Friday in Swedish.

**Usage:**
- Ask "är det fredag?" in the chat
- Bot responds with "JA!" and a link on Fridays
- Bot responds with "NEJ" on other days

### Other Plugins
See individual sections above for specific commands and usage.

## Development

### Setting Up Development Environment

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

3. Install pre-commit hooks:
```bash
pre-commit install
```

### Running Tests
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Support

For support:
1. Check the [Issues](https://github.com/yourusername/sopel-modules/issues) page
2. Open a new issue with detailed information about your problem
3. Contact the maintainer

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
