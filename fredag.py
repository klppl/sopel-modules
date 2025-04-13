"""Module that responds to questions about whether it's Friday or not in Swedish."""
from sopel import module
import re
import datetime
from typing import Pattern
from typing import Match

# Pre-compile the regex pattern for better performance
FRIDAY_PATTERN: Pattern[str] = re.compile(r"är\s+det\s+fredag\??", re.IGNORECASE)
FRIDAY_INDEX: int = 4  # Monday is 0, Sunday is 6
FRIDAY_URL: str = 'https://rebecca.blackfriday'

@module.rule('.*')
def fredag(bot, trigger) -> None:
    """
    Check if today is Friday and respond accordingly.
    
    Args:
        bot: The Sopel bot instance
        trigger: The message trigger containing the user's message
    """
    message: str = trigger.group(0)
    friday_match: Match[str] | None = FRIDAY_PATTERN.search(message)
    
    if friday_match:
        try:
            current_day: int = datetime.datetime.today().weekday()
            if current_day == FRIDAY_INDEX:
                bot.say(f'JA! {FRIDAY_URL}')
            else:
                bot.say('NEJ, det är inte fredag.')
        except Exception as e:
            bot.say('Ursäkta, jag kan inte kolla datum just nu.')
            bot.logger.error(f'Error checking weekday: {str(e)}')
