# coding=utf-8
"""
sopel_reddit.py
~~~~~~~~~~~~~~~

A Sopel plugin that fetches Reddit data via its public JSON endpoints.
When a Reddit URL is posted, the plugin retrieves the corresponding data
and formats it for display in IRC using a configurable template.

Configuration (via Sopel's configure command):
  [reddit]
      enabled = yes
      maxChars = 300
      linkThreadTemplate = [Reddit] /r/{subreddit} - {title} | {score} points | {comments} comments | {age}
      textThreadTemplate = [Reddit] /r/{subreddit} (Self) - {title} | {score} points | {age} | {extract}
      commentTemplate = [Reddit] Comment by {author}: {extract} | {score} points
      userTemplate = [Reddit] User: {name} | Karma: {link_karma} / {comment_karma}
"""

import re
import json
import datetime
import requests
from urllib.parse import urlparse
from sopel import plugin, tools


def configure(config):
    """
    Configure the Reddit plugin.
    """
    if config.option('Configure Reddit plugin?', False):
        config.define_section('reddit', 'Reddit plugin configuration')
        config.reddit.configure_setting('enabled', 'Enable Reddit lookups? (yes/no)')
        config.reddit.configure_setting('maxChars', 'Maximum characters for text extraction from Reddit posts/comments')
        config.reddit.configure_setting('linkThreadTemplate', 'Template for Reddit link threads')
        config.reddit.configure_setting('textThreadTemplate', 'Template for Reddit text threads (self-posts)')
        config.reddit.configure_setting('commentTemplate', 'Template for Reddit comments')
        config.reddit.configure_setting('userTemplate', 'Template for Reddit user information')


def setup(bot):
    if not hasattr(bot.config, 'reddit'):
        tools.logger.debug('Reddit plugin: no configuration found; using defaults')
    else:
        if not hasattr(bot.config.reddit, 'enabled'):
            bot.config.reddit.enabled = True
        if not hasattr(bot.config.reddit, 'maxChars'):
            bot.config.reddit.maxChars = 300
        if not hasattr(bot.config.reddit, 'linkThreadTemplate'):
            bot.config.reddit.linkThreadTemplate = "[Reddit] /r/{subreddit} - {title} | {score} points | {comments} comments | {age}"
        if not hasattr(bot.config.reddit, 'textThreadTemplate'):
            bot.config.reddit.textThreadTemplate = "[Reddit] /r/{subreddit} (Self) - {title} | {score} points | {age} | {extract}"
        if not hasattr(bot.config.reddit, 'commentTemplate'):
            bot.config.reddit.commentTemplate = "[Reddit] Comment by {author}: {extract} | {score} points"
        if not hasattr(bot.config.reddit, 'userTemplate'):
            bot.config.reddit.userTemplate = "[Reddit] User: {name} | Karma: {link_karma} / {comment_karma}"


@plugin.url(r'https?://(?:www\.)?reddit\.com/\S+')
def reddit_lookup(bot, trigger):
    """
    Given a Reddit URL, fetch the JSON data and display a formatted message.
    """
    url = trigger.group(0)
    enabled = getattr(bot.config.reddit, 'enabled', True)
    if not enabled:
        return

    # Define regex patterns for different Reddit URL types.
    patterns = {
        "thread": {
            "pattern": r"^/r/(?P<subreddit>[^/]+)/comments/(?P<thread>[^/]+)",
            "url": "https://www.reddit.com/r/{subreddit}/comments/{thread}.json",
        },
        "comment": {
            "pattern": r"^/r/(?P<subreddit>[^/]+)/comments/(?P<thread>[^/]+)/[^/]+/(?P<comment>\w+/?)$",
            "url": "https://www.reddit.com/r/{subreddit}/comments/{thread}/x/{comment}.json",
        },
        "user": {
            "pattern": r"^/u(?:ser)?/(?P<user>[^/]+)/?$",
            "url": "https://www.reddit.com/user/{user}/about.json",
        },
    }

    info = urlparse(url)
    link_type = None
    link_info = None
    data_url = None

    # Try to match the URL path against our patterns.
    for key, pattern in patterns.items():
        m = re.search(pattern["pattern"], info.path)
        if m:
            link_type = key
            link_info = m.groupdict()
            data_url = pattern["url"].format(**link_info)
            break

    if not link_type:
        tools.get_logger("reddit").debug("No matching Reddit URL pattern for %s", url)
        return

    # Use a proper User-Agent to avoid being blocked by Reddit.
    headers = {"User-Agent": "Sopel Reddit Plugin Bot"}
    try:
        resp = requests.get(data_url, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        bot.logger.error("Reddit request error: %s", e)
        return

    try:
        response = resp.json()
    except Exception as e:
        bot.logger.error("Error decoding Reddit JSON: %s", e)
        return

    data = {}
    extract = ""
    if response:
        try:
            if link_type == "thread":
                data = response[0]["data"]["children"][0]["data"]
            elif link_type == "comment":
                data = response[1]["data"]["children"][0]["data"]
                # Get the thread title from the first part of the response.
                data["title"] = response[0]["data"]["children"][0]["data"]["title"]
            elif link_type == "user":
                data = response["data"]
        except KeyError as e:
            bot.logger.error("Error parsing Reddit JSON: %s", e)
            return
    else:
        bot.logger.error("Empty Reddit JSON response")
        return

    # Process creation time and compute an 'age' string.
    try:
        created_utc = data.get("created_utc")
        created_dt = datetime.datetime.fromtimestamp(created_utc)
        created = created_dt.strftime("%Y-%m-%d")
        today = datetime.datetime.now()
        age_days = (today - created_dt).days
        if age_days == 0:
            age = "today"
        elif age_days == 1:
            age = "yesterday"
        else:
            if age_days < 365:
                age = f"{age_days}d ago"
            else:
                years = age_days // 365
                days = age_days % 365
                age = f"{years}y {days}d ago"
    except Exception:
        created = ""
        age = ""

    # For thread URLs, decide whether it's a self-post or a link.
    if link_type == "thread":
        if data.get("is_self"):
            # For self-posts, use the textThread template.
            link_type = "textThread"
            data["url"] = ""
            extract = data.get("selftext", "")
        else:
            link_type = "linkThread"
    elif link_type == "comment":
        extract = data.get("body", "")
    elif link_type == "user":
        # For user lookups, ensure a display name is present.
        data["name"] = data.get("name", data.get("subreddit", {}).get("display_name", ""))

    # Prepare variables for template formatting.
    template_vars = {
        "id": data.get("id", ""),
        "user": data.get("name", ""),
        "gold": data.get("is_gold", False),
        "mod": data.get("is_mod", False),
        "author": data.get("author", ""),
        "subreddit": data.get("subreddit", ""),
        "url": data.get("url", ""),
        "title": data.get("title", ""),
        "domain": data.get("domain", ""),
        "score": data.get("score", 0),
        "percent": "{}%".format(int(data.get("upvote_ratio", 0) * 100)) if data.get("upvote_ratio") is not None else "",
        "comments": "{:,}".format(data.get("num_comments", 0)) if data.get("num_comments") is not None else "",
        "created": created,
        "age": age,
        "link_karma": "{:,}".format(data.get("link_karma", 0)) if data.get("link_karma") is not None else "",
        "comment_karma": "{:,}".format(data.get("comment_karma", 0)) if data.get("comment_karma") is not None else "",
        "extract": extract,
    }

    # Truncate extract if it exceeds the maximum characters allowed.
    # Fix: Handle case where maxChars might be None
    max_chars = getattr(bot.config.reddit, "maxChars", 300)
    if max_chars is None:
        max_chars = 300
    
    if extract and len(extract) > max_chars:
        extract = extract[:max_chars - 3].rsplit(" ", 1)[0].rstrip(",.") + "..."
    template_vars["extract"] = extract

    # Determine which template to use based on the link type.
    config_key = link_type + "Template"
    template_str = getattr(bot.config.reddit, config_key, None)
    if not template_str:
        # Fallback defaults if not set in the config.
        if link_type == "linkThread":
            template_str = "[Reddit] /r/{subreddit} - {title} | {score} points | {comments} comments | {age}"
        elif link_type == "textThread":
            template_str = "[Reddit] /r/{subreddit} (Self) - {title} | {score} points | {age} | {extract}"
        elif link_type == "comment":
            template_str = "[Reddit] Comment by {author}: {extract} | {score} points"
        elif link_type == "user":
            template_str = "[Reddit] User: {name} | Karma: {link_karma} / {comment_karma}"
        else:
            template_str = "[Reddit] {title}"

    try:
        reply = template_str.format(**template_vars)
    except Exception as e:
        bot.logger.error("Error formatting Reddit template: %s", e)
        reply = template_vars.get("title", "")

    bot.say(reply)