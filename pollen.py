from sopel import module
import requests
from functools import lru_cache
import time
import re
from datetime import datetime, timedelta

# Cache for forecasts with timestamp
forecast_cache = {}
CACHE_DURATION = 3600  # 1 hour in seconds

@module.commands('pollen')
def pollen(bot, trigger):
    region_name = trigger.group(2) or "Sverige"  # Default to Sverige if no region specified
    is_default = not trigger.group(2)  # Check if this is the default case

    try:
        forecast = get_forecast(region_name)
        # Split the message into parts if it's too long
        parts = split_message(forecast)
        for part in parts:
            bot.say(part)
            time.sleep(1)  # Add delay between messages to prevent flooding
        
        # If this was the default case, show available cities
        if is_default:
            time.sleep(1)  # Add a small delay before showing cities
            regions = get_regions()
            region_names = sorted([item["name"] for item in regions])
            bot.say(f"Tillgängliga städer: .pollen {'|'.join(region_names)}")
    except requests.exceptions.RequestException:
        bot.say("Kunde inte hämta pollenprognos. Kontrollera din internetanslutning eller försök igen senare.")
    except Exception as e:
        bot.say(f"Ett oväntat fel uppstod: {str(e)}")

@module.commands('pollenhelp')
def pollen_help(bot, trigger):
    """Show help information for the pollen command"""
    help_text = (
        "Användning: .pollen [stad] - Visa pollenprognos för en specifik stad. "
        "Om ingen stad anges visas prognos för Sverige. "
        "För att se tillgängliga städer, skriv .pollen"
    )
    bot.say(help_text)

@lru_cache(maxsize=1)
def get_regions():
    """Cache the regions list to avoid repeated API calls"""
    regions_url = "https://api.pollenrapporten.se/v1/regions"
    response = requests.get(regions_url)
    response.raise_for_status()
    return response.json()["items"]

def get_forecast(region_name):
    """Get forecast for a region with caching"""
    current_time = time.time()
    
    # Check cache
    if region_name in forecast_cache:
        cached_data, timestamp = forecast_cache[region_name]
        if current_time - timestamp < CACHE_DURATION:
            return cached_data
    
    regions = get_regions()
    
    # Find the best matching region (case-insensitive, partial match)
    matching_regions = [
        item for item in regions 
        if region_name.lower() in item["name"].lower()
    ]
    
    if not matching_regions:
        region_names = [item["name"] for item in regions]
        return f"Hittar ingen prognos. Kör någon av följande: {', '.join(region_names)}"
    
    # If multiple matches, prefer exact match
    exact_match = next(
        (item for item in matching_regions if item["name"].lower() == region_name.lower()),
        matching_regions[0]  # Use first match if no exact match
    )
    
    forecasts_url = exact_match["forecasts"]
    forecasts_response = requests.get(forecasts_url)
    forecasts_response.raise_for_status()
    
    forecasts_data = forecasts_response.json()
    if not forecasts_data["items"]:
        return f"{exact_match['name']}: Ingen prognos tillgänglig just nu."
        
    forecast_item = forecasts_data["items"][0]
    forecast_text = forecast_item["text"]
    
    # Format the date range if available
    date_info = ""
    if "startDate" in forecast_item and "endDate" in forecast_item:
        start_date = datetime.strptime(forecast_item["startDate"], "%Y-%m-%d")
        end_date = datetime.strptime(forecast_item["endDate"], "%Y-%m-%d")
        date_info = f" ({start_date.strftime('%d/%m')}-{end_date.strftime('%d/%m')})"
    
    # Clean up the text (remove extra whitespace, newlines)
    forecast_text = re.sub(r'\s+', ' ', forecast_text).strip()
    result = f"{exact_match['name']}{date_info}: {forecast_text}"
    
    # Update cache
    forecast_cache[region_name] = (result, current_time)
    return result

def split_message(text, max_length=400):
    """Split a long message into multiple parts"""
    # First split by double newlines to preserve paragraph structure
    paragraphs = text.split('\n\n')
    parts = []
    current_part = []
    current_length = 0

    for paragraph in paragraphs:
        # Clean up the paragraph (remove extra whitespace, newlines)
        paragraph = re.sub(r'\s+', ' ', paragraph).strip()
        if not paragraph:
            continue

        # If adding this paragraph would exceed max_length, start a new part
        if current_length + len(paragraph) + 2 > max_length and current_part:
            parts.append(' '.join(current_part))
            current_part = []
            current_length = 0

        current_part.append(paragraph)
        current_length += len(paragraph) + 2  # +2 for the space between paragraphs

    # Add any remaining text
    if current_part:
        parts.append(' '.join(current_part))

    return parts
