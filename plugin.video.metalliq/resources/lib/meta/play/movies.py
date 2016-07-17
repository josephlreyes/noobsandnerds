import json

from xbmcswift2 import xbmc
import urllib

from meta import plugin, import_tmdb, LANG
from meta.utils.text import to_unicode, parse_year, to_utf8
from meta.utils.properties import set_property
from meta.info import get_movie_metadata
from meta.play.players import get_needed_langs, ADDON_SELECTOR
from meta.play.base import get_trakt_ids, active_players, action_cancel, action_play, on_play_video

from settings import SETTING_USE_SIMPLE_SELECTOR, SETTING_MOVIES_DEFAULT_PLAYER, SETTING_MOVIES_DEFAULT_PLAYER_FROM_LIBRARY, SETTING_MOVIES_DEFAULT_PLAYER_FROM_CONTEXT
from language import get_string as _

def play_movie(tmdb_id, mode):  
    import_tmdb()
        
    # Get players to use
    if mode == 'select':
        play_plugin = ADDON_SELECTOR.id
    elif mode == 'context':
        play_plugin = plugin.get_setting(SETTING_MOVIES_DEFAULT_PLAYER_FROM_CONTEXT)
    elif mode == 'library':
        play_plugin = plugin.get_setting(SETTING_MOVIES_DEFAULT_PLAYER_FROM_LIBRARY)
    elif mode == 'default':
        play_plugin = plugin.get_setting(SETTING_MOVIES_DEFAULT_PLAYER)
    else:
        play_plugin = mode
    players = active_players("movies")
    players = [p for p in players if p.id == play_plugin] or players
    if not players:
        xbmc.executebuiltin( "Action(Info)")
        action_cancel()
        return
    
    # Get movie data from TMDB
    movie = tmdb.Movies(tmdb_id).info(language=LANG)
    movie_info = get_movie_metadata(movie)

    # Get movie ids from Trakt
    trakt_ids = get_trakt_ids("tmdb", tmdb_id, movie['original_title'],
                    "movie", parse_year(movie['release_date']))
    
    # Get parameters
    params = {}
    for lang in get_needed_langs(players):
        if lang == LANG:
            tmdb_data = movie
        else:
            tmdb_data = tmdb.Movies(tmdb_id).info(language=lang)
        params[lang] = get_movie_parameters(tmdb_data)
        if trakt_ids != None:
            params[lang].update(trakt_ids)
        params[lang]['info'] = movie_info
        params[lang] = to_unicode(params[lang])

    # Go for it
    link = on_play_video(mode, players, params, trakt_ids)
    if link:
        movie = tmdb.Movies(tmdb_id).info(language=LANG)
        action_play({
            'label': movie_info['title'],
            'path': link,
            'info': movie_info,
            'is_playable': True,
            'info_type': 'video',
            'thumbnail': movie_info['poster'],
            'poster': movie_info['poster'],
            'properties' : {'fanart_image' : movie_info['fanart']},
        })
        
def get_movie_parameters(movie):
    parameters = {}

    parameters['id'] = movie['id']
    parameters['imdb'] = movie['imdb_id']
    parameters['title'] = movie['title']
    parameters['urltitle'] = urllib.quote(parameters['title'])
    parameters['sorttitle'] = parameters['title']
    articles = ['a ', 'A ', 'An ', 'an ', 'The ', 'the ']
    for article in articles:
        if to_utf8(parameters['title']).startswith(article): parameters['sorttitle'] = to_utf8(parameters['title']).replace(article,'')
    parameters['shorttitle'] = parameters['title'][1:-1]
    parameters['original_title'] = movie['original_title']
    parameters['date'] = movie['release_date']
    parameters['year'] = parse_year(movie['release_date'])
    parameters['name'] = u'%s (%s)' % (parameters['title'], parameters['year'])
    parameters['urlname'] = urllib.quote(parameters['name'])
    
    return parameters
