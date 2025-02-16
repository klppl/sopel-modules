# coding=utf-8
"""
sopel_imgur.py
~~~~~~~~~~~~~~~~

A Sopel plugin that fetches Imgur data via its API.
When an Imgur URL is posted, the plugin retrieves details about
an image or album and formats it for display in IRC using a
configurable template.

Configuration (via Sopel’s configure command):
  [imgur]
      enabled = yes
      clientid = YOUR_IMGUR_CLIENT_ID
      albumTemplate = [Imgur] Album: {title} | {image_count} images | {view_count} views
      imageTemplate = [Imgur] Image: {title} | {type} | {width}x{height} | {file_size} | {view_count} views
"""

import re
import json
import requests
from urllib.parse import urlparse
from sopel import plugin, tools

# Create a module-level logger.
logger = tools.get_logger('imgur')


def configure(config):
    """
    Configure the Imgur plugin.
    """
    if config.option('Configure Imgur plugin?', False):
        config.define_section('imgur', 'Imgur plugin configuration')
        config.imgur.configure_setting('enabled', 'Enable Imgur lookups? (yes/no)')
        config.imgur.configure_setting('clientid', 'Imgur Client ID (required)')
        config.imgur.configure_setting('albumTemplate', 'Template for Imgur albums')
        config.imgur.configure_setting('imageTemplate', 'Template for Imgur images')


def setup(bot):
    if not hasattr(bot.config, 'imgur'):
        logger.debug('Imgur plugin: no configuration found; using defaults')
    else:
        if not hasattr(bot.config.imgur, 'enabled'):
            bot.config.imgur.enabled = True
        if not hasattr(bot.config.imgur, 'clientid'):
            bot.config.imgur.clientid = ""
        if not hasattr(bot.config.imgur, 'albumTemplate'):
            bot.config.imgur.albumTemplate = "[Imgur] Album: {title} | {image_count} images | {view_count} views"
        if not hasattr(bot.config.imgur, 'imageTemplate'):
            bot.config.imgur.imageTemplate = "[Imgur] Image: {title} | {type} | {width}x{height} | {file_size} | {view_count} views"


def is_valid_imgur_id(imgur_id):
    """
    Tests if the provided string is a valid Imgur identifier,
    which is typically alphanumeric.
    """
    return bool(re.match(r"^[a-zA-Z0-9]+$", imgur_id))


def get_readable_file_size(num_bytes):
    """
    Convert a file size in bytes to a human-readable string.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f}{unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f}PB"


def handle_imgur_album(bot, url, path):
    """
    Retrieves and formats album information from the Imgur API.
    """
    clientid = bot.config.imgur.clientid
    if not clientid:
        logger.error("Imgur plugin: clientid not set")
        return

    # Extract album ID from the URL path.
    album_id = ""
    if path.startswith("/a/"):
        album_id = path.split("/a/")[1]
    elif path.startswith("/gallery/"):
        album_id = path.split("/gallery/")[1]
    # Remove any query string.
    if "?" in album_id:
        album_id = album_id.split("?")[0]
    # If the album id contains hyphens (a slug), extract the last part.
    if "-" in album_id:
        album_id = album_id.split("-")[-1]
    if not is_valid_imgur_id(album_id):
        logger.error("Imgur plugin: Invalid album ID")
        return

    logger.debug("Imgur plugin: found album id %s", album_id)
    headers = {"Authorization": f"Client-ID {clientid}"}
    api_url = f"https://api.imgur.com/3/album/{album_id}"
    try:
        resp = requests.get(api_url, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logger.error("Imgur plugin: Error fetching album: %s", e)
        return

    try:
        data = resp.json().get("data")
    except Exception as e:
        logger.error("Imgur plugin: Error parsing album JSON: %s", e)
        return

    if data:
        template_vars = {
            "title": data.get("title") or "",
            "section": data.get("section") or "",
            "view_count": "{:,}".format(data.get("views", 0)),
            "image_count": "{:,}".format(data.get("images_count", 0)),
            "nsfw": data.get("nsfw", False),
            "description": data.get("description") or "",
        }
        # Use a fallback template if config value is missing.
        template_str = bot.config.imgur.albumTemplate or "[Imgur] Album: {title} | {image_count} images | {view_count} views"
        try:
            result = template_str.format(**template_vars)
        except Exception as e:
            logger.error("Imgur plugin: Error formatting album template: %s", e)
            result = ""
        return result
    else:
        logger.error("Imgur plugin: Album API returned unexpected results")
        return


def handle_imgur_image(bot, url, path):
    clientid = bot.config.imgur.clientid
    if not clientid:
        logger.error("Imgur plugin: clientid not set")
        return

    if "." in path:
        image_id = path.lstrip("/").split(".")[0]
    else:
        image_id = path.lstrip("/")

    if not is_valid_imgur_id(image_id):
        logger.error("Imgur plugin: Invalid image ID")
        return

    logger.debug("Imgur plugin: found image id %s", image_id)
    headers = {"Authorization": f"Client-ID {clientid}"}
    api_url = f"https://api.imgur.com/3/image/{image_id}"
    try:
        resp = requests.get(api_url, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logger.error("Imgur plugin: Error fetching image: %s", e)
        return

    try:
        data = resp.json().get("data")
    except Exception as e:
        logger.error("Imgur plugin: Error parsing image JSON: %s", e)
        return

    if data:
        file_size = get_readable_file_size(data.get("size", 0))
        album_id = data.get("album")
        album_link = f"https://imgur.com/a/{album_id}" if album_id else ""
        template_vars = {
            "title": data.get("title") or "",
            "type": data.get("type") or "",
            "nsfw": data.get("nsfw", False),
            "width": data.get("width", 0),
            "height": data.get("height", 0),
            "view_count": "{:,}".format(data.get("views", 0)),
            "file_size": file_size,
            "section": data.get("section") or "",
            "album_link": album_link,
            "description": data.get("description") or "",
            "datetime": data.get("datetime") or "",
            "link": data.get("link") or "",
        }
        template_str = bot.config.imgur.imageTemplate or "[Imgur] Image: {title} | {type} | {width}x{height} | {file_size} | {view_count} views | Album: {album_link}"
        try:
            result = template_str.format(**template_vars)
        except Exception as e:
            logger.error("Imgur plugin: Error formatting image template: %s", e)
            result = ""
        return result
    else:
        logger.error("Imgur plugin: Image API returned unexpected results")
        return



@plugin.url(r'https?://(?:www\.)?imgur\.com/\S+')
def imgur_lookup(bot, trigger):
    """
    Handles Imgur URLs on imgur.com.
    Distinguishes between albums/galleries and direct image links.
    """
    url = trigger.group(0)
    enabled = getattr(bot.config.imgur, 'enabled', True)
    if not enabled:
        return

    parsed = urlparse(url)
    path = parsed.path

    # Check if the URL indicates an album or gallery.
    if path.startswith("/a/") or path.startswith("/gallery/"):
        result = handle_imgur_album(bot, url, path)
    else:
        result = handle_imgur_image(bot, url, path)

    if result:
        bot.say(result)


@plugin.url(r'https?://i\.imgur\.com/\S+')
def imgur_image_lookup(bot, trigger):
    """
    Handles direct image URLs from i.imgur.com.
    """
    url = trigger.group(0)
    enabled = getattr(bot.config.imgur, 'enabled', True)
    if not enabled:
        return

    parsed = urlparse(url)
    path = parsed.path
    result = handle_imgur_image(bot, url, path)
    if result:
        bot.say(result)
