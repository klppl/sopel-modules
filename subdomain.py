from sopel import module
import requests

@module.commands('subdomain')
def subdomain(bot, trigger):
    domain = trigger.group(2)
    if not domain:
        bot.say('Usage: .subdomain <domain>')
        return
      
    try:
        response = requests.get(f'https://api.subdomain.center/?domain={domain}')
        subdomains = response.json()
    except Exception as e:
        bot.say(f'Error while fetching subdomains: {e}')
        return

    if not subdomains:
        bot.say('No subdomains found.')
        return

    subdomains_text = "\n".join(subdomains)
    
    try:
        response = requests.post('http://0x0.st', files={'file': ('subdomains.txt', subdomains_text)})
        upload_url = response.text.strip()
    except Exception as e:
        bot.say(f'Error while uploading to 0x0.st: {e}')
        return

    bot.say(f'Subdomains: {upload_url}')
