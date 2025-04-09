from sopel import module
from sopel import formatting
import requests
import json
import sqlite3
import os

def get_instrument_from_db(instrument_name, instrument_type=None):
    """
    Search the local avanza_data.db for an instrument matching the given name.
    If instrument_type is specified, filter by that type.
    Returns a tuple (id, name, currency, instrument_type) if found, otherwise None.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "avanza_data.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if instrument_type:
        query = """
            SELECT id, name, currency, instrumentType FROM orderbooklist 
            WHERE instrumentType = ? AND name LIKE ? COLLATE NOCASE
        """
        cursor.execute(query, (instrument_type, '%' + instrument_name + '%'))
    else:
        query = """
            SELECT id, name, currency, instrumentType FROM orderbooklist 
            WHERE name LIKE ? COLLATE NOCASE
        """
        cursor.execute(query, ('%' + instrument_name + '%',))
    
    row = cursor.fetchone()
    conn.close()
    return row

def format_price_change(value, suffix='%'):
    """Format price changes with colors and proper suffix."""
    try:
        if float(value) < 0:
            return formatting.color(f"{value}{suffix}", formatting.colors.RED)
        elif float(value) > 0:
            return formatting.color(f"{value}{suffix}", formatting.colors.GREEN)
        return f"{value}{suffix}"
    except (ValueError, TypeError):
        return f"{value}{suffix}"

def get_instrument_details(instrument_id):
    """Fetch detailed information for an instrument from Avanza."""
    try:
        url = f"https://www.avanza.se/_mobile/market/orderbooklist/{instrument_id}"
        response = requests.get(url, timeout=10)
        data = json.loads(response.text)
        return data[0] if data else None
    except Exception:
        return None

@module.commands('aktie', 'a', 'stock')
def stock_prices(bot, trigger):
    """Look up a stock and display its price details."""
    stock_query = trigger.group(2)
    if not stock_query:
        bot.say("Please specify a stock name!")
        return

    stock = get_instrument_from_db(stock_query, 'STOCK')
    if not stock:
        bot.say("No stock found with that name!")
        return

    stock_id, stock_name, stock_currency, _ = stock
    stock_data = get_instrument_details(stock_id)
    
    if not stock_data:
        bot.say("Could not fetch stock data.")
        return

    # Basic price information
    last_price = stock_data.get("lastPrice", "N/A")
    change_percent = format_price_change(stock_data.get("changePercent", "N/A"))
    change_value = stock_data.get("change", "N/A")
    
    # Volume and price range
    volume = stock_data.get("totalVolumeTraded", "N/A")
    low_price = stock_data.get("lowestPrice", "N/A")
    high_price = stock_data.get("highestPrice", "N/A")
    
    # Historical data
    price_3m = stock_data.get("priceThreeMonthsAgo", "N/A")
    try:
        change_3m = round((float(last_price) - float(price_3m)) / float(price_3m) * 100, 1)
        change_3m = format_price_change(change_3m)
    except Exception:
        change_3m = "N/A"

    # Additional market data
    market_data = []
    market_cap = stock_data.get("marketCapitalization")
    if market_cap and market_cap != "N/A":
        market_data.append(f"MCap: {market_cap}")
    
    pe_ratio = stock_data.get("priceEarningsRatio")
    if pe_ratio and pe_ratio != "N/A":
        market_data.append(f"P/E: {pe_ratio}")
    
    dividend_yield = stock_data.get("dividendYield")
    if dividend_yield and dividend_yield != "N/A":
        market_data.append(f"Div: {dividend_yield}%")

    market_info = " | " + " | ".join(market_data) if market_data else ""

    bot.say(f"{stock_name} | {last_price} {stock_currency} | "
            f"Today: {change_percent} ({change_value} {stock_currency}) | "
            f"3M: {change_3m} | Range: {low_price} - {high_price} {stock_currency} | "
            f"Vol: {volume}{market_info}")

@module.commands('fond', 'f', 'fund')
def fund_prices(bot, trigger):
    """Look up a fund and display its price details."""
    fund_query = trigger.group(2)
    if not fund_query:
        bot.say("Please specify a fund name!")
        return

    fund = get_instrument_from_db(fund_query, 'FUND')
    if not fund:
        bot.say("No fund found with that name!")
        return

    fund_id, fund_name, fund_currency, _ = fund
    fund_data = get_instrument_details(fund_id)
    
    if not fund_data:
        bot.say("Could not fetch fund data.")
        return

    # Basic price information
    last_price = fund_data.get("lastPrice", "N/A")
    change_percent = format_price_change(fund_data.get("changePercent", "N/A"))
    change_value = fund_data.get("change", "N/A")
    
    # Fund specific data
    management_fee = fund_data.get("managementFee", "N/A")
    risk_level = fund_data.get("riskLevel", "N/A")
    category = fund_data.get("category", "N/A")

    bot.say(f"{fund_name} | {last_price} {fund_currency} | "
            f"Today: {change_percent} ({change_value} {fund_currency}) | "
            f"Fee: {management_fee}% | Risk: {risk_level} | Category: {category}")

@module.commands('etf', 'e')
def etf_prices(bot, trigger):
    """Look up an ETF and display its price details."""
    etf_query = trigger.group(2)
    if not etf_query:
        bot.say("Please specify an ETF name!")
        return

    etf = get_instrument_from_db(etf_query, 'EXCHANGE_TRADED_FUND')
    if not etf:
        bot.say("No ETF found with that name!")
        return

    etf_id, etf_name, etf_currency, _ = etf
    etf_data = get_instrument_details(etf_id)
    
    if not etf_data:
        bot.say("Could not fetch ETF data.")
        return

    # Basic price information
    last_price = etf_data.get("lastPrice", "N/A")
    change_percent = format_price_change(etf_data.get("changePercent", "N/A"))
    change_value = etf_data.get("change", "N/A")
    
    # ETF specific data
    volume = etf_data.get("totalVolumeTraded", "N/A")
    category = etf_data.get("category", "N/A")
    replication_method = etf_data.get("replicationMethod", "N/A")

    bot.say(f"{etf_name} | {last_price} {etf_currency} | "
            f"Today: {change_percent} ({change_value} {etf_currency}) | "
            f"Vol: {volume} | Category: {category} | Replication: {replication_method}")

@module.commands('index', 'i')
def index_prices(bot, trigger):
    """Display selected index data."""
    indices = {
        "OMXS30": "19002",
        "NASDAQ": "19006",
        "DAX": "18981",
        "Nikkei225": "18997",
        "S&P500": "19007",
        "FTSE100": "18982"
    }
    
    for index_name, index_id in indices.items():
        index_data = get_instrument_details(index_id)
        if not index_data:
            continue

        name = index_data.get("name", index_name)
        last_price = index_data.get("lastPrice", "N/A")
        currency = index_data.get("currency", "N/A")
        change_percent = format_price_change(index_data.get("changePercent", "N/A"))
        change_value = index_data.get("change", "N/A")
        
        bot.say(f"{name} | {last_price} {currency} | Today: {change_percent} ({change_value} {currency})")

@module.commands('avanza', 'av')
def search_instruments(bot, trigger):
    """Search for any type of instrument on Avanza."""
    query = trigger.group(2)
    if not query:
        bot.say("Please specify a search term!")
        return

    results = []
    instrument_types = ['STOCK', 'FUND', 'EXCHANGE_TRADED_FUND', 'BOND', 'CERTIFICATE']
    
    for inst_type in instrument_types:
        result = get_instrument_from_db(query, inst_type)
        if result:
            results.append(f"{result[1]} ({inst_type})")
            if len(results) >= 5:  # Limit to 5 results
                break

    if results:
        bot.say("Found: " + ", ".join(results))
    else:
        bot.say("No instruments found matching your search.")

@module.commands('cert', 'c')
def certificate_prices(bot, trigger):
    """Look up a certificate and display its price details."""
    cert_query = trigger.group(2)
    if not cert_query:
        bot.say("Please specify a certificate name!")
        return

    cert = get_instrument_from_db(cert_query, 'CERTIFICATE')
    if not cert:
        bot.say("No certificate found with that name!")
        return

    cert_id, cert_name, cert_currency, _ = cert
    cert_data = get_instrument_details(cert_id)
    
    if not cert_data:
        bot.say("Could not fetch certificate data.")
        return

    # Basic price information
    last_price = cert_data.get("lastPrice", "N/A")
    change_percent = format_price_change(cert_data.get("changePercent", "N/A"))
    change_value = cert_data.get("change", "N/A")
    
    # Certificate specific data
    volume = cert_data.get("totalVolumeTraded", "N/A")
    category = cert_data.get("category", "N/A")
    leverage = cert_data.get("leverage", "N/A")

    bot.say(f"{cert_name} | {last_price} {cert_currency} | "
            f"Today: {change_percent} ({change_value} {cert_currency}) | "
            f"Vol: {volume} | Category: {category} | Leverage: {leverage}x")
