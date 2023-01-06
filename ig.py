import sopel
import re
import requests
from bs4 import BeautifulSoup

@sopel.module.rule('.*((?:https?:)?//(?:www\.)?instagram\.com/p/.*).*')
def process_message(bot, trigger):
    # Check if the message contains an Instagram URL
    match = re.search('.*((?:https?:)?//(?:www\.)?instagram\.com/p/.*).*', trigger.group(0))
    if match:
        # Get the URL from the message
        url = match.group(1)

        # Add the http: scheme if it is missing
        if not url.startswith('http'):
            url = 'http:' + url

        # Make an HTTP GET request to the URL
        response = requests.get(url)

        # Parse the HTML of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the og:title and og:description meta tags
        title_meta = soup.find('meta', {'property': 'og:title'})
        description_meta = soup.find('meta', {'property': 'og:description'})
        image_meta = soup.find('meta', {'property': 'og:image'})

        # Extract the values from the meta tags
        title = title_meta['content'] if title_meta else 'No title found'
        description = description_meta['content'] if description_meta else 'No description found'
        #image = image_meta['content'] if image_meta else 'No image found'
        #extract the direct url to image and upload it to imgur
        #image = image_meta['content'] if image_meta else 'No image found'

        # remove the query strings from image
        #image = image.split('?')[0]

        # Respond with the values
        bot.say(f'{title}')
