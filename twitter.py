# coding=utf-8
"""
sopel_twitter_oembed
~~~~~~~~~~~~~~~~~~~~

A Sopel plugin that fetches Twitter data via the oEmbed API.
When a tweet URL is posted, this plugin retrieves the tweet’s embedded HTML,
extracts the text, and formats it for display in IRC using a configurable template.

Configuration (via Sopel’s configure command):
  [twitter]
      enabled = yes
      template = {name} (@{nick}): {content} - {date}

The default template uses these variables:
  - content: the tweet text
  - name: the tweet author’s full name
  - nick: the tweet author’s username
  - date: the date portion of the tweet
"""

import re
import requests
from bs4 import BeautifulSoup
from sopel import plugin, tools

def configure(config):
    """
    Configure the Twitter plugin.
    """
    if config.option('Configure Twitter plugin?', False):
        config.define_section('twitter', 'Twitter plugin configuration')
        config.twitter.configure_setting('enabled', 'Enable Twitter lookups? (yes/no)')
        config.twitter.configure_setting(
            'template',
            'Template for tweet output. '
            'Available variables: content, name, nick, date'
        )

def setup(bot):
    if not hasattr(bot.config, 'twitter'):
        tools.logger.debug('Twitter plugin: no configuration found; using defaults')
    else:
        if not hasattr(bot.config.twitter, 'enabled'):
            bot.config.twitter.enabled = True
        if not hasattr(bot.config.twitter, 'template'):
            bot.config.twitter.template = "{name} (@{nick}): {content} - {date}"

@plugin.url(r'https?://(?:www\.)?(?:mobile\.)?(?:twitter|x)\.com/\S+/status/\d+')
def twitter_oembed(bot, trigger):
    url = trigger.group(0)
    enabled = getattr(bot.config.twitter, 'enabled', True)
    if not enabled:
        return

    # Build the oEmbed API URL
    api_url = "https://publish.twitter.com/oembed?url={0}&omit_script=True".format(url)
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        bot.logger.error("Twitter oEmbed request error: %s", e)
        return

    try:
        data = response.json()
    except Exception as e:
        bot.logger.error("Error decoding JSON from Twitter oEmbed: %s", e)
        return

    html = data.get("html")
    if not html:
        return

    # Extract text from the returned HTML using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ").strip()

    # Expected format from Twitter oEmbed: "<content> — <name> (<nick>) <date>"
    match = re.match(r"(.*) — (.*) \((.*)\) (.*)", text)
    if match:
        content = match.group(1).strip()
        name = match.group(2).strip()
        nick = match.group(3).strip()
        date = match.group(4).strip()
    else:
        # Fallback if pattern matching fails
        content = text
        name = ""
        nick = ""
        date = ""

    template_str = getattr(
        bot.config.twitter,
        'template',
        "{name} (@{nick}): {content} - {date}"
    )

    try:
        formatted = template_str.format(content=content, name=name, nick=nick, date=date)
    except Exception as e:
        bot.logger.error("Error formatting template: %s", e)
        formatted = text

    if formatted:
        bot.say(formatted)
    else:
        bot.say(text)
