import sopel
import re
import time
import instaloader
from urllib.parse import urlparse

# Cache to store recent requests
CACHE = {}
CACHE_DURATION = 300  # 5 minutes

def extract_shortcode(instagram_url):
    """
    Extract the shortcode from the Instagram URL.
    Expected URL format: https://www.instagram.com/p/SHORTCODE/...
    """
    parsed_url = urlparse(instagram_url)
    segments = parsed_url.path.split('/')
    if "p" in segments:
        idx = segments.index("p")
        if idx + 1 < len(segments):
            return segments[idx + 1]
    return None

def fetch_instagram_post_data(url):
    shortcode = extract_shortcode(url)
    if not shortcode:
        return None

    L = instaloader.Instaloader()
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
    except Exception as e:
        print(f"Error fetching post data with Instaloader: {e}")
        return None

    username = post.owner_username
    likes_count = post.likes
    comments_count = post.comments
    caption = post.caption if post.caption else ""
    # Truncate caption to the first 140 characters for a concise message
    if len(caption) > 140:
        caption = caption[:140] + "..."
        
    return {
        "username": username,
        "likes_count": likes_count,
        "comments_count": comments_count,
        "caption": caption
    }

@sopel.module.rule('.*((?:https?:)?//(?:www\.)?instagram\.com/(?:p|reel)/[^/]+).*')
def process_message(bot, trigger):
    try:
        # Check if the message contains an Instagram URL
        match = re.search('.*((?:https?:)?//(?:www\.)?instagram\.com/(?:p|reel)/[^/]+).*', trigger.group(0))
        if not match:
            return

        # Get the URL from the message
        url = match.group(1)
        
        # Check cache first
        current_time = time.time()
        if url in CACHE and current_time - CACHE[url]['timestamp'] < CACHE_DURATION:
            bot.say(CACHE[url]['response'])
            return

        # Get Instagram data
        data = fetch_instagram_post_data(url)
        
        if not data:
            bot.say('Could not fetch Instagram post data')
            return

        # Format the response
        response_parts = ['📸']
        
        if data['username']:
            response_parts.append(f'@{data["username"]}')
            
        if data['caption']:
            response_parts.append(data['caption'])
            
        response_parts.append(f'❤️ {data["likes_count"]:,} likes')
        response_parts.append(f'💬 {data["comments_count"]:,} comments')
        
        response_text = ' | '.join(response_parts)

        # Cache the response
        CACHE[url] = {
            'response': response_text,
            'timestamp': current_time
        }

        # Respond with the values
        bot.say(response_text)

    except Exception as e:
        bot.say(f'An error occurred: {str(e)}')
