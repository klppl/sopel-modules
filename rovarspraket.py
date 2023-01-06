import sopel

@sopel.module.commands('rövarspråket')
def rovarspraket(bot, trigger):
    # Get the text to convert from the command
    text = trigger.group(2)

    # Convert the text to Rövarspråket
    converted_text = ''
    for c in text:
        if c.isalpha() and c not in 'aeiouAEIOU':
            # Add the character and its "rövarspråket" representation
            converted_text += c + 'o' + c.lower()
        else:
            # Just add the character
            converted_text += c

    # Send the converted text back to the channel
    bot.say(converted_text)

