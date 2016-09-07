#!/usr/bin/python
# -*- coding: utf-8 -*-
if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import os
import time
import shutil
import traceback
from xbmcswift2 import xbmcplugin, xbmcvfs
from meta import plugin
from meta.utils.properties import get_property, set_property, clear_property
from meta.gui import dialogs
from meta.play import updater
from meta.play.base import active_players, active_channelers
from meta.play.players import get_players, ADDON_SELECTOR 
from meta.play.channelers import get_channelers, ADDON_PICKER
from meta.navigation.base import get_icon_path, get_background_path
import meta.navigation.movies
import meta.navigation.tvshows
import meta.navigation.live
import meta.navigation.music
import meta.navigation.lists
import meta.library.tvshows
import meta.library.movies
import meta.library.music
import meta.library.live
from language import get_string as _
from settings import *

FORCE = plugin.get_setting(SETTING_FORCE_VIEW, bool)
VIEW  = plugin.get_setting(SETTING_MAIN_VIEW, int)

addonid = 'plugin.video.metalliq'

@plugin.route('/')
def root():
    """ Root directory """
    items = [
        {
            'label': _("Movies"),
            'path': plugin.url_for("movies"),
            'icon': get_icon_path("movies"),
        },
        {
            'label': _("TV shows"),
            'path': plugin.url_for("tv"),
            'icon': get_icon_path("tv"),
        },
        {
            'label': _("Music"),
            'path': plugin.url_for("music"),
            'icon': get_icon_path("music"),
        },
        {
            'label': _("Live"),
            'path': plugin.url_for("live"),
            'icon': get_icon_path("live"),
        },
        {
            'label': _("Lists"),
            'path': plugin.url_for("lists"),
            'icon': get_icon_path("lists"),
        },
        {
            'label': _("Search"),
            'path': plugin.url_for("root_search"),
            'icon': get_icon_path("search"),
        }
    ]
    fanart = plugin.addon.getAddonInfo('fanart')
    for item in items:
        item['properties'] = {'fanart_image' : get_background_path()}
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items

@plugin.route('/clear_cache')
def clear_cache():
    """ Clear all caches """
    for filename in os.listdir(plugin.storage_path):
        file_path = os.path.join(plugin.storage_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception, e:
            traceback.print_exc()
    plugin.notify(msg='Cache', title='Deleted', delay=5000, image=get_icon_path("metalliq"))

@plugin.route('/update_library')
def update_library():
    is_updating = get_property("updating_library")
    now = time.time()
    if is_updating and now - int(is_updating) < 120:
        plugin.log.debug("Skipping library update")
        return
    if plugin.get_setting(SETTING_LIBRARY_UPDATES, converter=bool) == True:
        #plugin.notify(msg=_('Library'), title=_('Updating'), delay=5000, image=get_icon_path("metalliq"))
        try:
            set_property("updating_library", int(now))
            meta.library.tvshows.update_library()
            meta.library.movies.update_library()
            meta.library.music.update_library()
        finally:
            clear_property("updating_library")
    else:
        #plugin.notify(msg=_('Library'), title=_('Not updating'), delay=5000, image=get_icon_path("metalliq"))
        clear_property("updating_library")

@plugin.route('/authenticate_trakt')
def trakt_authenticate():
    from trakt import trakt
    trakt.trakt_authenticate()

@plugin.route('/settings/players/<media>')
def settings_set_players(media):
    playericon = get_icon_path("player")
    medias = ["movies","tvshows","musicvideos","music","live"]
    if media == "all":
        for media in medias:
            mediatype = media.replace('es','e').replace('ws','w').replace('all','').replace('os','o').replace('vs','v s')
            players = get_players(media)
            selected = [p.id for p in players]
            if selected is not None:
                if media == "movies":
                    plugin.set_setting(SETTING_MOVIES_ENABLED_PLAYERS, selected)
                elif media == "tvshows":
                    plugin.set_setting(SETTING_TV_ENABLED_PLAYERS, selected)
                elif media == "musicvideos":
                    plugin.set_setting(SETTING_MUSICVIDEOS_ENABLED_PLAYERS, selected)
                elif media == "music":
                    plugin.set_setting(SETTING_MUSIC_ENABLED_PLAYERS, selected)
                elif media == "live":
                    plugin.set_setting(SETTING_LIVE_ENABLED_PLAYERS, selected)
                else:
                    raise Exception("invalid parameter %s" % media)
            plugin.notify(msg=_('All '+mediatype+' players'), title=_('Enabled'), delay=1000, image=get_icon_path("player"))
        plugin.notify(msg=_('All players'), title=_('Enabled'), delay=1000, image=get_icon_path("player"))
        return True
    elif media == "tvportal":
        players = get_players("live")
        selected = [p.id for p in players]
        plugin.set_setting(SETTING_LIVE_ENABLED_PLAYERS, selected)
        return
    else:
        mediatype = media.replace('es','e ').replace('ws','w ').replace('all','').replace('ve','ve ').replace('_','')
        players = get_players(media)
        players = sorted(players,key=lambda player: player.clean_title.lower())
        version = xbmc.getInfoLabel('System.BuildVersion')
        selected = None
        if version.startswith('16') or version.startswith('17'):
            msg = "Do you want to enable all "+mediatype+"players?"
            if dialogs.yesno(_("Enable all "+mediatype+"players"), _(msg)):
                selected = [p.id for p in players]
            else:
                result = dialogs.multiselect(_("Select "+mediatype+"players to enable"), [p.clean_title for p in players])
                if result is not None:
                    selected = [players[i].id for i in result]
        else:
            selected = None
            msg = "Kodi 16 is required for multi-selection. Do you want to enable all "+mediatype+"players instead?"
            if dialogs.yesno(_("Enable all "+mediatype+"players"), _(msg)):
                selected = [p.id for p in players]
            else:
                result = dialogs.multichoice(_("Select "+mediatype+"players to enable"), [p.clean_title for p in players])
                if result is not None:
                    selected = [players[i].id for i in result]
        if selected is not None:
            if media == "movies":
                plugin.set_setting(SETTING_MOVIES_ENABLED_PLAYERS, selected)
            elif media == "tvshows":
                plugin.set_setting(SETTING_TV_ENABLED_PLAYERS, selected)
            elif media == "musicvideos":
                plugin.set_setting(SETTING_MUSICVIDEOS_ENABLED_PLAYERS, selected)
            elif media == "music":
                plugin.set_setting(SETTING_MUSIC_ENABLED_PLAYERS, selected)
            elif media == "live":
                plugin.set_setting(SETTING_LIVE_ENABLED_PLAYERS, selected)
            else:
                raise Exception("invalid parameter %s" % media)
        plugin.notify(msg=_('All '+mediatype+'players'), title=_('Updated'), delay=1000, image=get_icon_path("player"))
    plugin.open_settings()

@plugin.route('/settings/channelers')
def settings_set_channelers():
    medias = ["movies","tvshows","live"]
    for media in medias:
        channelers = get_channelers(media)
        selected = [p.id for p in channelers]
        if selected is not None:
            if media == "movies":
                plugin.set_setting(SETTING_MOVIES_ENABLED_CHANNELERS, selected)
            elif media == "tvshows":
                plugin.set_setting(SETTING_TV_ENABLED_CHANNELERS, selected)
            elif media == "live":
                plugin.set_setting(SETTING_LIVE_ENABLED_CHANNELERS, selected)
            else:
                raise Exception("invalid parameter %s" % media)
    print "MetalliQ Guidance: Movie, TV and Live players enabled"
    return True

@plugin.route('/settings/default_channeler/<media>')
def settings_set_default_channeler(media):
    channelers = active_channelers(media)
    channelers.insert(0, ADDON_PICKER)
    media = media.replace('es','e').replace('ws','w').replace('all','').replace('os','o').replace('vs','v s')
    selection = dialogs.select(_("Select default "+media+" player for guide"), [p.title for p in channelers])
    if selection >= 0:
        selected = channelers[selection].id
        if media == "movies":
            plugin.set_setting(SETTING_MOVIES_DEFAULT_CHANNELER, selected)
        elif media == "tvshows":
            plugin.set_setting(SETTING_TV_DEFAULT_CHANNELER, selected)
        elif media == "music":
            plugin.set_setting(SETTING_MUSIC_DEFAULT_CHANNELER, selected)
        elif media == "musicvideos":
            plugin.set_setting(SETTING_MUSICVIDEOS_DEFAULT_CHANNELER, selected)
        elif media == "live":
            plugin.set_setting(SETTING_LIVE_DEFAULT_CHANNELER, selected)
        else:
            raise Exception("invalid parameter %s" % media)

@plugin.route('/settings/default_player/<media>')
def settings_set_default_player(media):
    players = active_players(media)
    players.insert(0, ADDON_SELECTOR)
    selection = dialogs.select(_("Select player"), [p.title for p in players])
    if selection >= 0:
        selected = players[selection].id
        if media == "movies":
            plugin.set_setting(SETTING_MOVIES_DEFAULT_PLAYER, selected)
        elif media == "tvshows":
            plugin.set_setting(SETTING_TV_DEFAULT_PLAYER, selected)
        elif media == "music":
            plugin.set_setting(SETTING_MUSIC_DEFAULT_PLAYER, selected)
        elif media == "musicvideos":
            plugin.set_setting(SETTING_MUSICVIDEOS_DEFAULT_PLAYER, selected)
        elif media == "live":
            plugin.set_setting(SETTING_LIVE_DEFAULT_PLAYER, selected)
        else:
            raise Exception("invalid parameter %s" % media)
    plugin.open_settings()

@plugin.route('/settings/default_player_fromlib/<media>')
def settings_set_default_player_fromlib(media):
    players = active_players(media)
    players.insert(0, ADDON_SELECTOR)
    selection = dialogs.select(_("Select player"), [p.title for p in players])
    if selection >= 0:
        selected = players[selection].id
        if media == "movies":
            plugin.set_setting(SETTING_MOVIES_DEFAULT_PLAYER_FROM_LIBRARY, selected)
        elif media == "tvshows":
            plugin.set_setting(SETTING_TV_DEFAULT_PLAYER_FROM_LIBRARY, selected)
        elif media == "musicvideos":
            plugin.set_setting(SETTING_MUSICVIDEOS_DEFAULT_PLAYER_FROM_LIBRARY, selected)
        elif media == "music":
            plugin.set_setting(SETTING_MUSIC_DEFAULT_PLAYER_FROM_LIBRARY, selected)
        elif media == "live":
            plugin.set_setting(SETTING_LIVE_DEFAULT_PLAYER_FROM_LIBRARY, selected)
        else:
            raise Exception("invalid parameter %s" % media)
    plugin.open_settings()

@plugin.route('/settings/default_player_fromcontext/<media>')
def settings_set_default_player_fromcontext(media):
    players = active_players(media)
    players.insert(0, ADDON_SELECTOR)
    selection = dialogs.select(_("Select player"), [p.title for p in players])
    if selection >= 0:
        selected = players[selection].id
        if media == "movies":
            plugin.set_setting(SETTING_MOVIES_DEFAULT_PLAYER_FROM_CONTEXT, selected)
        elif media == "tvshows":
            plugin.set_setting(SETTING_TV_DEFAULT_PLAYER_FROM_CONTEXT, selected)
        elif media == "musicvideos":
            plugin.set_setting(SETTING_MUSICVIDEOS_DEFAULT_PLAYER_FROM_CONTEXT, selected)
        elif media == "music":
            plugin.set_setting(SETTING_MUSIC_DEFAULT_PLAYER_FROM_CONTEXT, selected)
        elif media == "live":
            plugin.set_setting(SETTING_LIVE_DEFAULT_PLAYER_FROM_CONTEXT, selected)
        else:
            raise Exception("invalid parameter %s" % media)
    plugin.open_settings()

@plugin.route('/update_players')
def update_players():
    url = plugin.get_setting(SETTING_PLAYERS_UPDATE_URL, converter=unicode)
    if updater.update_players(url):
        plugin.notify(msg=_('Players'), title=_('Updated'), delay=1000, image=get_icon_path("player"))
    else:
        plugin.notify(msg=_('Players update'), title=_('Failed'), delay=1000, image=get_icon_path("player"))
    plugin.open_settings()

@plugin.route('/totalsetup')
def total_setup():
    plugin.notify(msg='Total Setup', title='Started', delay=1000, image=get_icon_path("metalliq"))
    if player_setup() == True:
        pass
    if source_setup() == True:
        pass
    plugin.notify(msg='Total Setup', title='Completed', delay=5000, image=get_icon_path("metalliq"))

@plugin.route('/playersetup')
def player_setup():
    xbmc.executebuiltin('SetProperty(running,totalmetalliq,home)')
    url = "https://api.github.com/repos/OpenELEQ/verified-metalliq-players/zipball"
    if updater.update_players(url): plugin.notify(msg=_('Players'), title=_('Updated'), delay=1000, image=get_icon_path("player"))
    else: plugin.notify(msg=_('Players update'), title=_('Failed'), delay=1000, image=get_icon_path("player"))
    xbmc.executebuiltin("RunPlugin(plugin://plugin.video.metalliq/settings/players/all/)")
    xbmc.executebuiltin('ClearProperty(running,home)')
    return True

@plugin.route('/sourcesetup')
def source_setup():
    movielibraryfolder = plugin.get_setting(SETTING_MOVIES_LIBRARY_FOLDER)
    try:
        meta.library.movies.auto_movie_setup(movielibraryfolder)
        plugin.notify(msg=_('Movies library folder'), title=_('Setup Done'), delay=1000, image=get_icon_path("movies"))
    except:
        plugin.notify(msg=_('Movies library folder'), title=_('Setup Failed'), delay=1000, image=get_icon_path("movies"))
    tvlibraryfolder = plugin.get_setting(SETTING_TV_LIBRARY_FOLDER)
    try:
        meta.library.tvshows.auto_tvshows_setup(tvlibraryfolder)
        plugin.notify(msg=_('TV shows library folder'), title=_('Setup Done'), delay=1000, image=get_icon_path("tv"))
    except:
        plugin.notify(msg=_('TV shows library folder'), title=_('Setup Failed'), delay=1000, image=get_icon_path("tv"))
    musiclibraryfolder = plugin.get_setting(SETTING_MUSIC_LIBRARY_FOLDER)
    try:
        meta.library.music.auto_music_setup(musiclibraryfolder)
        plugin.notify(msg=_('Music library folder'), title=_('Setup Done'), delay=1000, image=get_icon_path("music"))
    except:
        plugin.notify(msg=_('Music library folder'), title=_('Setup Failed'), delay=1000, image=get_icon_path("music"))
    livelibraryfolder = plugin.get_setting(SETTING_LIVE_LIBRARY_FOLDER)
    try:
        meta.library.live.auto_live_setup(livelibraryfolder)
        plugin.notify(msg=_('Live library folder'), title=_('Setup Done'), delay=1000, image=get_icon_path("live"))
    except:
        plugin.notify(msg=_('Live library folder'), title=_('Setup Failed'), delay=1000, image=get_icon_path("live"))
    return True

@plugin.route('/test')
def playlist_folders_setup():
    movies_playlist_folder = plugin.get_setting(SETTING_MOVIES_PLAYLIST_FOLDER)
    if not xbmcvfs.exists(movies_playlist_folder): xbmcvfs.mkdir(movies_playlist_folder)
    elif xbmcvfs.exists(movies_playlist_folder): plugin.notify(msg='Movie playlist folder', title='Already exists', delay=1000, image=get_icon_path("lists"))
    else: plugin.notify(msg='Movie playlist folder creation', title='Failed', delay=1000, image=get_icon_path("lists"))
    tv_playlist_folder = plugin.get_setting(SETTING_TV_PLAYLIST_FOLDER)
    if not xbmcvfs.exists(tv_playlist_folder): xbmcvfs.mkdir(tv_playlist_folder)
    elif xbmcvfs.exists(tv_playlist_folder): plugin.notify(msg='TVShow playlist folder', title='Already exists', delay=1000, image=get_icon_path("lists"))
    else: plugin.notify(msg='TVShow playlist folder creation', title='Failed', delay=1000, image=get_icon_path("lists"))
    music_playlist_folder = plugin.get_setting(SETTING_MUSIC_PLAYLIST_FOLDER)
    if not xbmcvfs.exists(music_playlist_folder): xbmcvfs.mkdir(music_playlist_folder)
    elif xbmcvfs.exists(music_playlist_folder): plugin.notify(msg='Music playlist folder', title='Already exists', delay=1000, image=get_icon_path("lists"))
    else: plugin.notify(msg='Music playlist folder creation', title='Failed', delay=1000, image=get_icon_path("lists"))
    live_playlist_folder = plugin.get_setting(SETTING_LIVE_PLAYLIST_FOLDER)
    if not xbmcvfs.exists(live_playlist_folder): xbmcvfs.mkdir(live_playlist_folder)
    elif xbmcvfs.exists(live_playlist_folder): plugin.notify(msg='Live playlist folder', title='Already exists', delay=1000, image=get_icon_path("lists"))
    else: plugin.notify(msg='Live playlist folder creation', title='Failed', delay=1000, image=get_icon_path("lists"))
    plugin.notify(msg='Playlists folder creation', title='Completed', delay=1000, image=get_icon_path("lists"))
    return True

@plugin.route('/search')
def root_search():
    """ Search directory """
    items = [
        {
            'label': "All",
            'path': plugin.url_for(root_search_term, page='1'),
            'icon': get_icon_path("search"),
        },
        {
            'label': _("Movies") + ": " + _("Search (Trakt)"),
            'path': plugin.url_for("trakt_movies_search", page='1'),
            'icon': get_icon_path("movies"),
        },
        {
            'label': _("Movies") + ": " + _("Search (TMDb)"),
            'path': plugin.url_for("tmdb_movies_search", page='1'),
            'icon': get_icon_path("movies"),
        },
        {
            'label': _("TV shows") + ": " + _("Search (Trakt)"),
            'path': plugin.url_for("trakt_tv_search", page='1'),
            'icon': get_icon_path("tv"),
        },
        {
            'label': _("TV shows") + ": " + _("Search (TMDb)"),
            'path': plugin.url_for("tmdb_tv_search"),
            'icon': get_icon_path("tv"),
        },
        {
            'label': _("TV shows") + ": " + _("Search (TVDb)"),
            'path': plugin.url_for("tvdb_tv_search"),
            'icon': get_icon_path("tv"),
        },
        {
            'label': _("Music") + ": " + _("Search artist"),
            'path': plugin.url_for("music_search_artist"),
            'icon': get_icon_path("music"),
        },
        {
            'label': _("Music") + ": " + _("Search album"),
            'path': plugin.url_for("music_search_album"),
            'icon': get_icon_path("music"),
        },
        {
            'label': _("Music") + ": " + _("Search track"),
            'path': plugin.url_for("music_search_track"),
            'icon': get_icon_path("music"),
        },
        {
            'label': _("Live") + ": " + _("Search"),
            'path': plugin.url_for("live_search"),
            'icon': get_icon_path("live"),
        },
        {
            'label': _("Lists") + ": " + _("Search"),
            'path': plugin.url_for("lists_trakt_search_for_lists"),
            'icon': get_icon_path("lists"),
        }
    ]
    fanart = plugin.addon.getAddonInfo('fanart')
    for item in items:
        item['properties'] = {'fanart_image' : get_background_path()}
    return items

@plugin.route('/search/<term>/<page>', options = {"term": "None"})
def root_search_term(term, page):
    if term == "None":
        # Get search keyword
        search_entered = plugin.keyboard(heading=_("search for"))
        if not search_entered:
            return
    else:
        search_entered = term
    items = [
        {
            'label': "All" + ": " + search_entered,
            'path': plugin.url_for(root_search_term, term=search_entered, page='1'),
            'icon': get_icon_path("search"),
        },
        {
            'label': _("Movies") + " - " + _("Search (Trakt)") + ": " + search_entered,
            'path': plugin.url_for("trakt_movies_search_term", term=search_entered, page='1'),
            'icon': get_icon_path("movies"),
        },
        {
            'label': _("Movies") + " - " + _("Search (TMDb)") + ": " + search_entered,
            'path': plugin.url_for("tmdb_movies_search_term", term=search_entered, page='1'),
            'icon': get_icon_path("movies"),
        },
        {
            'label': _("TV shows") + " - " + _("Search (Trakt)") + ": " + search_entered,
            'path': plugin.url_for("trakt_tv_search_term", term=search_entered, page='1'),
            'icon': get_icon_path("tv"),
        },
        {
            'label': _("TV shows") + " - " + _("Search (TMDb)") + ": " + search_entered,
            'path': plugin.url_for("tmdb_tv_search_term", term=search_entered, page='1'),
            'icon': get_icon_path("tv"),
        },
        {
            'label': _("TV shows") + " - " + _("Search (TVDb)") + ": " + search_entered,
            'path': plugin.url_for("tvdb_tv_search_term", term=search_entered, page='1'),
            'icon': get_icon_path("tv"),
        },
        {
            'label': _("Music") + " - " + _("Search artist") + ": " + search_entered,
            'path': plugin.url_for("music_search_artist_term", term=search_entered, page='1'),
            'icon': get_icon_path("music"),
        },
        {
            'label': _("Music") + " - " + _("Search album") + ": " + search_entered,
            'path': plugin.url_for("music_search_album_term", term=search_entered, page='1'),
            'icon': get_icon_path("music"),
        },
        {
            'label': _("Music") + " - " + _("Search track") + ": " + search_entered,
            'path': plugin.url_for("music_search_track_term", term=search_entered, page='1'),
            'icon': get_icon_path("music"),
        },
        {
            'label': _("Live") + " - " + _("Search") + ": " + search_entered,
            'path': plugin.url_for("live_search_term", term=search_entered),
            'icon': get_icon_path("live"),
        },
        {
            'label': _("Lists") + " - " + _("Search") + ": " + search_entered,
            'path': plugin.url_for("lists_search_for_lists_term", term=search_entered, page='1'),
            'icon': get_icon_path("lists"),
        }
    ]
    fanart = plugin.addon.getAddonInfo('fanart')
    for item in items:
        item['properties'] = {'fanart_image' : get_background_path()}
    return items

@plugin.route('/toggle')
def toggle_context_toggle():
    if xbmc.getCondVisibility("Skin.HasSetting(Toggling)") != True: plugin.notify(msg="Toggling", title="Switched on", delay=5000, image=get_icon_path("metalliq"))
    else: plugin.notify(msg="Toggling", title="Switched off", delay=5000, image=get_icon_path("metalliq"))
    xbmc.executebuiltin("Skin.ToggleSetting(Toggling)")

@plugin.route('/context')
def toggle_context_player():
    if xbmc.getCondVisibility("Skin.HasSetting(Contexting)") != True: plugin.notify(msg="Context player", title="Switched off", delay=5000, image=get_icon_path("metalliq"))
    else: plugin.notify(msg="Context player", title="Switched on", delay=5000, image=get_icon_path("metalliq"))
    xbmc.executebuiltin("Skin.ToggleSetting(Contexting)")

@plugin.route('/toggle/acceleration')
def toggle_hardware_acceleration():
    if xbmc.getCondVisibility("System.Platform.Android") == 1:
        if xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"videoplayer.useamcodec"}, "id":1}') == '{"id":1,"jsonrpc":"2.0","result":{"value":true}}': xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"videoplayer.useamcodec","value":false}, "id":1}')
        elif xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"videoplayer.useamcodec"}, "id":1}') == '{"id":1,"jsonrpc":"2.0","result":{"value":false}}': xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"videoplayer.useamcodec","value":true}, "id":1}')
        else: pass
        if xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"videoplayer.usestagefright"}, "id":1}') == '{"id":1,"jsonrpc":"2.0","result":{"value":true}}': xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"videoplayer.usestagefright","value":false}, "id":1}')
        elif xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"videoplayer.usestagefright"}, "id":1}') == '{"id":1,"jsonrpc":"2.0","result":{"value":false}}': xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"videoplayer.usestagefright","value":true}, "id":1}')
        else: pass
        if xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"videoplayer.usemediacodec"}, "id":1}') == '{"id":1,"jsonrpc":"2.0","result":{"value":true}}': xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"videoplayer.usemediacodec","value":false}, "id":1}')
        elif xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"videoplayer.usemediacodec"}, "id":1}') == '{"id":1,"jsonrpc":"2.0","result":{"value":false}}': xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"videoplayer.usemediacodec","value":true}, "id":1}')
        else: pass
        if xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"videoplayer.usemediacodecsurface"}, "id":1}') == '{"id":1,"jsonrpc":"2.0","result":{"value":true}}': xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"videoplayer.usemediacodecsurface","value":false}, "id":1}')
        elif xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"videoplayer.usemediacodecsurface"}, "id":1}') == '{"id":1,"jsonrpc":"2.0","result":{"value":false}}': xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"videoplayer.usemediacodecsurface","value":true}, "id":1}')
        else: pass
    if xbmc.getCondVisibility("System.Platform.Linux.RaspberryPi") == 1:
        if xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"videoplayer.useomxplayer"}, "id":1}') == '{"id":1,"jsonrpc":"2.0","result":{"value":true}}': xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"videoplayer.useomxplayer","value":false}, "id":1}')
        elif xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"videoplayer.useomxplayer"}, "id":1}') == '{"id":1,"jsonrpc":"2.0","result":{"value":false}}': xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"videoplayer.useomxplayer","value":true}, "id":1}')
        else: pass
        if xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"videoplayer.usemmal"}, "id":1}') == '{"id":1,"jsonrpc":"2.0","result":{"value":true}}': xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"videoplayer.usemmal","value":false}, "id":1}')
        elif xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"videoplayer.usemmal"}, "id":1}') == '{"id":1,"jsonrpc":"2.0","result":{"value":false}}': xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"videoplayer.usemmal","value":true}, "id":1}')
        else: pass
    if xbmc.getCondVisibility("System.Platform.Windows") == 1:
        response = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"videoplayer.usedxva2"}, "id":1}')
        if xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"videoplayer.usedxva2"}, "id":1}') == '{"id":1,"jsonrpc":"2.0","result":{"value":true}}': xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"videoplayer.usedxva2","value":false}, "id":1}')
        elif xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"videoplayer.usedxva2"}, "id":1}') == '{"id":1,"jsonrpc":"2.0","result":{"value":false}}': xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"videoplayer.usedxva2","value":true}, "id":1}')
        else: pass

@plugin.route('/toggle/skin')
def toggle_between_skins():
    if xbmc.getCondVisibility("Skin.HasSetting(Contexting)") != True: contexting = False
    else: contexting = True
    if xbmc.getCondVisibility("Skin.HasSetting(Toggling)") != True: toggling = False
    else: toggling = True
    current_skin = str(xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"lookandfeel.skin"}, "id":1}')).replace('{"id":1,"jsonrpc":"2.0","result":{"value":"','').replace('"}}','')
    primary_skin = plugin.get_setting(SETTING_PRIMARY_SKIN, converter=str)
    alternate_skin = plugin.get_setting(SETTING_ALTERNATE_SKIN, converter=str)
    if primary_skin == "": plugin.set_setting(SETTING_PRIMARY_SKIN, current_skin)
    if alternate_skin == "": 
        if primary_skin != "skin.confluence": plugin.set_setting(SETTING_ALTERNATE_SKIN, "skin.confluence")
        else: plugin.notify(msg="Alternate skin", title="Not set", delay=5000, image=get_icon_path("metalliq")), openSettings(addonid, 5.5)
    if primary_skin != alternate_skin and primary_skin != "" and alternate_skin != "" and xbmc.getCondVisibility('System.HasAddon(%s)' % primary_skin) and xbmc.getCondVisibility('System.HasAddon(%s)' % alternate_skin):
        if current_skin != primary_skin: 
            xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"lookandfeel.skin","value":"%s"}, "id":1}' % primary_skin)
            xbmc.executebuiltin('SetFocus(11)')
            xbmc.executebuiltin('Action(Select)')
        else: 
            xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"lookandfeel.skin","value":"%s"}, "id":1}' % alternate_skin)
            xbmc.executebuiltin('SetFocus(11)')
            xbmc.executebuiltin('Action(Select)')
        if toggling == False: xbmc.executebuiltin('Skin.Reset(Toggling)')
        else: xbmc.executebuiltin('Skin.SetBool(Toggling)')
        if contexting == False: xbmc.executebuiltin('Skin.Reset(Contexting)')
        else: xbmc.executebuiltin('Skin.SetBool(Contexting)')

@plugin.route('/export')
def export_library():
    export_movies_library()
    export_tv_library()

@plugin.route('/export/movies')
def export_movies_library():
    folder_path = plugin.get_setting(SETTING_MOVIES_LIBRARY_FOLDER)
    if not xbmcvfs.exists(folder_path): return plugin.notify(msg='Movies folder', title='Absent', delay=5000, image=get_icon_path("movies"))
    ids = ""
    movies = xbmcvfs.listdir(folder_path)[0]
    if len(movies) < 1: return plugin.notify(msg='Movies folder', title='Empty', delay=5000, image=get_icon_path("movies"))
    else : 
        for movie in movies: ids = ids + str(movie) + '\n'
    movies_backup_file_path = "special://profile/addon_data/plugin.video.metalliq/movies_to_add.bak"
    if xbmcvfs.exists(movies_backup_file_path): os.remove(xbmc.translatePath(movies_backup_file_path))
    if not xbmcvfs.exists(movies_backup_file_path):
        batch_add_file = xbmcvfs.File(movies_backup_file_path, 'w')
        batch_add_file.write(ids)
        batch_add_file.close()
    plugin.notify(msg="Movies", title="Backed up", delay=5000, image=get_icon_path("movies"))

@plugin.route('/export/tv')
def export_tv_library():
    folder_path = plugin.get_setting(SETTING_TV_LIBRARY_FOLDER)
    if not xbmcvfs.exists(folder_path): return plugin.notify(msg='TVShows folder', title='Absent', delay=5000, image=get_icon_path("tv"))
    ids = ""
    shows = xbmcvfs.listdir(folder_path)[0]
    if len(shows) < 1: return plugin.notify(msg='TVShows folder', title='Empty', delay=5000, image=get_icon_path("tv"))
    else : 
        for show in shows: ids = ids + str(show) + '\n'
    shows_backup_file_path = "special://profile/addon_data/plugin.video.metalliq/shows_to_add.bak"
    if xbmcvfs.exists(shows_backup_file_path): os.remove(xbmc.translatePath(shows_backup_file_path))
    if not xbmcvfs.exists(shows_backup_file_path):
        batch_add_file = xbmcvfs.File(shows_backup_file_path, 'w')
        batch_add_file.write(ids)
        batch_add_file.close()
    plugin.notify(msg="TVShows", title="Backed up", delay=5000, image=get_icon_path("tv"))

@plugin.route('/play/<label>')
def play_by_label(label):
    types = [_("Movies"), _("TV shows")]
    selection = dialogs.select(_("Choose season"), [item for item in types])
    if selection == 0: xbmc.executebuiltin("RunPlugin(plugin://plugin.video.metalliq/movies/play_by_name/{0}/en)".format(label))
    else: xbmc.executebuiltin("RunPlugin(plugin://plugin.video.metalliq/tv/play_by_name_only/{0}/en)".format(label))

@plugin.route('/settings')
def settings_general():
    openSettings(addonid, 0.0)

@plugin.route('/settings/movies')
def settings_movies():
    openSettings(addonid, 1.2)

@plugin.route('/settings/tv')
def settings_tv():
    openSettings(addonid, 2.2)

@plugin.route('/settings/music')
def settings_music():
    openSettings(addonid, 3.3)

@plugin.route('/settings/live')
def settings_live():
    openSettings(addonid, 4.2)

@plugin.route('/settings/advanced/')
def settings_advanced():
    openSettings(addonid, 5.0)

@plugin.route('/settings/toggling/')
def settings_toggling():
    openSettings(addonid, 5.3)

@plugin.route('/settings/appearance/')
def settings_appearance():
    openSettings(addonid, 6.0)

def openSettings(addonid, focus=None):
    try:
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % addonid)
        value1, value2 = str(focus).split('.')
        xbmc.executebuiltin('SetFocus(%d)' % (int(value1) + 100))
        xbmc.executebuiltin('SetFocus(%d)' % (int(value2) + 200))
    except:
        return

#########   Main    #########

def main():
    if '/movies' in sys.argv[0]:
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    elif '/tv' in sys.argv[0]:
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    elif '/music' in sys.argv[0]:
        xbmcplugin.setContent(int(sys.argv[1]), 'musicvideos')
    elif '/live' in sys.argv[0]:
        xbmcplugin.setContent(int(sys.argv[1]), 'LiveTV')
    elif '/list' in sys.argv[0]:
        xbmcplugin.setContent(int(sys.argv[1]), 'playlists')
    else:
        pass
    plugin.run()

if __name__ == '__main__':
    main()