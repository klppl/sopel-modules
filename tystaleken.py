import sopel

tysta_leken_in_progress = False

@sopel.module.commands('tystaleken')
def tysta_leken(bot, trigger):
    # Start the truth or dare game
    bot.say('Tysta leken börjar nu!')

    # Set the flag to indicate that the game is in progress
    global tysta_leken_in_progress
    tysta_leken_in_progress = True

    # Save the channel where the game is being played
    global tysta_leken_channel
    tysta_leken_channel = trigger.sender

@sopel.module.rule('.*')
def process_message(bot, trigger):
    # Check if the game is in progress
    global tysta_leken_in_progress
    if tysta_leken_in_progress:
        # Check if the message was sent in the correct channel
        global tysta_leken_channel
        if trigger.sender == tysta_leken_channel:
            # Respond with "You lost <nickname>"
            bot.say(f'Du förlorade {trigger.nick}')

            # End the game
            tysta_leken_in_progress = False
