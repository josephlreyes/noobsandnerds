import re
import json
from xbmcswift2 import xbmc
import urllib
from meta import plugin, import_tmdb, import_tvdb, create_tvdb, LANG
from meta.gui import dialogs
from meta.utils.properties import set_property
from meta.utils.text import to_unicode, to_utf8
from meta.library.tvshows import get_player_plugin_from_library
from meta.info import get_tvshow_metadata_tvdb, get_season_metadata_tvdb, get_episode_metadata_tvdb
from meta.play.players import get_needed_langs, ADDON_SELECTOR
from meta.play.channelers import get_needed_langs, ADDON_PICKER
from meta.play.base import get_trakt_ids, active_players, active_channelers, action_cancel, action_play, on_play_video
from settings import SETTING_USE_SIMPLE_SELECTOR, SETTING_TV_DEFAULT_PLAYER, SETTING_TV_DEFAULT_PLAYER_FROM_LIBRARY, SETTING_TV_DEFAULT_PLAYER_FROM_LIBRARY, SETTING_TV_DEFAULT_PLAYER_FROM_CONTEXT, SETTING_TV_DEFAULT_CHANNELER
from language import get_string as _

def play_episode(id, season, episode, mode):  
    import_tvdb()
    id = int(id)
    season = int(season)
    episode = int(episode)
    # Get database id
    dbid = xbmc.getInfoLabel("ListItem.DBID")
    try:
        dbid = int(dbid)
    except:
        dbid = None
    # Get show data from TVDB
    show = tvdb[id]
    show_info = get_tvshow_metadata_tvdb(show, banners=False)
    # Get players to use
    if mode == 'select':
        play_plugin = ADDON_SELECTOR.id
    elif mode == 'context':
        play_plugin = plugin.get_setting(SETTING_TV_DEFAULT_PLAYER_FROM_CONTEXT)
    elif mode == 'library':
        play_plugin = get_player_plugin_from_library(id)
        if not play_plugin or play_plugin == "default":
            play_plugin = plugin.get_setting(SETTING_TV_DEFAULT_PLAYER_FROM_LIBRARY)
    elif mode == 'default':
        play_plugin = plugin.get_setting(SETTING_TV_DEFAULT_PLAYER)
    else:
        play_plugin = mode
    players = active_players("tvshows", filters = {'network': show.get('network')})
    players = [p for p in players if p.id == play_plugin] or players
    if not players:
        xbmc.executebuiltin( "Action(Info)")
        action_cancel()
        return
    # Get show ids from Trakt
    trakt_ids = get_trakt_ids("tvdb", id, show['seriesname'],
                    "show", show.get('year', 0))
    # Get parameters
    params = {}
    for lang in get_needed_langs(players):
        if lang == LANG:
            tvdb_data = show
        else:
            tvdb_data = create_tvdb(lang)[id]
        if tvdb_data['seriesname'] is None:
            continue
        episode_parameters = get_episode_parameters(tvdb_data, season, episode)
        if episode_parameters is not None:
            params[lang] = episode_parameters
        else:
            msg = "{0} {1} - S{1}E{2}".format(_("No tvdb information found for"), show['seriesname'], season, episode)
            dialogs.ok(_("Episode info not found"), msg)
            return
        if trakt_ids != None:
            params[lang].update(trakt_ids)
        params[lang]['info'] = show_info
        params[lang] = to_unicode(params[lang])
    # Go for it
    link = on_play_video(mode, players, params, trakt_ids)
    if link:
        # set properties
        set_property("data", json.dumps({'dbid': dbid, 'tvdb': id, 
            'season': season, 'episode': episode}))
        # Play
        season_info = get_season_metadata_tvdb(show_info, show[season], banners=False)
        episode_info = get_episode_metadata_tvdb(season_info, show[season][episode])
        action_play({
            'label': episode_info['title'],
            'path': link,
            'info': episode_info,
            'is_playable': True,
            'info_type': 'video',
            'thumbnail': episode_info['poster'],
            'poster': episode_info['poster'],
            'properties' : {'fanart_image' : episode_info['fanart']},
        })

def play_episode_from_guide(id, season, episode, mode):  
    import_tvdb()
    id = int(id)
    season = int(season)
    episode = int(episode)
    dbid = xbmc.getInfoLabel("ListItem.DBID")
    try:
        dbid = int(dbid)
    except:
        dbid = None
    show = tvdb[id]
    show_info = get_tvshow_metadata_tvdb(show, banners=False)
    if mode == 'select':
        play_plugin = ADDON_PICKER.id
    elif mode == 'default':
        play_plugin = plugin.get_setting(SETTING_TV_DEFAULT_CHANNELER)
    else:
        play_plugin = mode
    channelers = active_channelers("tvshows", filters = {'network': show.get('network')})
    channelers = [p for p in channelers if p.id == play_plugin] or channelers
    if not channelers:
        xbmc.executebuiltin( "Action(Info)")
        action_cancel()
        return
    trakt_ids = get_trakt_ids("tvdb", id, show['seriesname'],
                    "show", show.get('year', 0))
    params = {}
    for lang in get_needed_langs(channelers):
        if lang == LANG:
            tvdb_data = show
        else:
            tvdb_data = create_tvdb(lang)[id]
        if tvdb_data['seriesname'] is None:
            continue
        episode_parameters = get_episode_parameters(tvdb_data, season, episode)
        if episode_parameters is not None:
            params[lang] = episode_parameters
        else:
            msg = "{0} {1} - S{1}E{2}".format(_("No tvdb information found for"), show['seriesname'], season, episode)
            dialogs.ok(_("Episode info not found"), msg)
            return
        if trakt_ids != None:
            params[lang].update(trakt_ids)
        params[lang]['info'] = show_info
        params[lang] = to_unicode(params[lang])
    link = on_play_video(mode, channelers, params, trakt_ids)
    if link:
        set_property("data", json.dumps({'dbid': dbid, 'tvdb': id, 
            'season': season, 'episode': episode}))
        season_info = get_season_metadata_tvdb(show_info, show[season], banners=False)
        episode_info = get_episode_metadata_tvdb(season_info, show[season][episode])
        action_play({
            'label': episode_info['title'],
            'path': link,
            'info': episode_info,
            'is_playable': True,
            'info_type': 'video',
            'thumbnail': episode_info['poster'],
            'poster': episode_info['poster'],
            'properties' : {'fanart_image' : episode_info['fanart']},
        })

def get_episode_parameters(show, season, episode):
    import_tmdb()
    if season in show and episode in show[season]:
        season_obj = show[season]
        episode_obj = show[season][episode]
    else:
        return
    # Get parameters
    parameters = {'id': show['id'], 'season': season, 'episode': episode}
    show_info = get_tvshow_metadata_tvdb(show, banners=True)
    network = show.get('network', '')
    parameters['network'] = network
    if network:
        parameters['network_clean'] = re.sub("(\(.*?\))", "", network).strip()
    else:
        parameters['network_clean'] = network
    parameters['showname'] = show['seriesname']
    parameters['clearname'] = re.sub("(\(.*?\))", "", show['seriesname']).strip()
    parameters['urlname'] = urllib.quote(to_utf8(parameters['clearname']))
    articles = ['a ', 'A ', 'An ', 'an ', 'The ', 'the ']
    parameters['sortname'] = parameters['clearname']
    for article in articles:
        if to_utf8(parameters['clearname']).startswith(article): parameters['sortname'] = to_utf8(parameters['clearname']).replace(article,'')
    parameters['shortname'] = parameters['clearname'][1:-1]
    try:
        parameters['absolute_number'] = int(episode_obj.get('absolute_number'))
    except:
        parameters['absolute_number'] = "na"
    parameters['title'] = episode_obj.get('episodename', str(episode))
    parameters['urltitle'] = urllib.quote(to_utf8(parameters['title']))
    parameters['firstaired'] = episode_obj.get('firstaired')
    parameters['year'] = show.get('year', 0)
    parameters['imdb'] = show.get('imdb_id', '')
    parameters['epid'] = episode_obj.get('id')
#    parameters['score'] = show['rating']
#    parameters['vote_count'] = show['ratingcount']
#    parameters['runtime'] = show['runtime']
#    parameters['duration'] = int(show['runtime']) * 60
#    parameters['plot'] = show['overview']
#    parameters['banner'] = "http://thetvdb.com/banners/graphical/" + str(show['id']) + "-g2.jpg"
    parameters['poster'] = "http://thetvdb.com/banners/posters/" + str(show['id']) + "-2.jpg"
    parameters['fanart'] = "http://thetvdb.com/banners/fanart/original/" + str(show['id']) + "-2.jpg"
    parameters['thumbnail'] = "http://thetvdb.com/banners/episodes/" + str(show['id']) + "/" + str(parameters['epid']) + ".jpg"
#    parameters['trailer'] = "plugin://script.extendedinfo/?info=playtvtrailer&tvdb_id=" + str(show['id'])
    try:
        genre = [x for x in show['genre'].split('|') if not x == '']
    except:
        genre = []
    parameters['genre'] = " / ".join(genre)
    is_anime = False
    if parameters['absolute_number'] and parameters['absolute_number'] != '0' and "animation" in parameters['genre'].lower():
        tmdb_results = tmdb.Find(show['id']).info(external_source="tvdb_id") or {}
        for tmdb_show in tmdb_results.get("tv_results", []):
            if "JP" in tmdb_show['origin_country']:
                is_anime = True
    if is_anime:
        parameters['name'] = u'{showname} {absolute_number}'.format(**parameters)
    else:
        parameters['name'] = u'{showname} S{season:02d}E{episode:02d}'.format(**parameters)
    return parameters
