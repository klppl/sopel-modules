import sopel
import tmdbsimple as tmdb

@sopel.module.commands('movie')
def tmdb_command(bot, trigger):
    movie_title = trigger.group(2)

    tmdb.API_KEY = 'API_KEY'
    search = tmdb.Search()
    response = search.movie(query=movie_title)

    try:
        result = response['results'][0]
        tmdb_id = result['id']
        url = f'https://www.2embed.to/embed/tmdb/movie?id={tmdb_id}'
        
        bot.say(url)
    except IndexError:
        bot.say("Sorry, nothing found.")
