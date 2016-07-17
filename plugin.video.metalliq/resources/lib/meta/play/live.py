import re
import urllib
from xbmcswift2 import xbmc
from meta import plugin, LANG
from meta.utils.text import to_unicode
from meta.library.live import get_player_plugin_from_library
from meta.play.players import get_needed_langs, ADDON_SELECTOR
from meta.play.base import active_players, action_cancel, action_play, on_play_video

from settings import SETTING_USE_SIMPLE_SELECTOR, SETTING_LIVE_DEFAULT_PLAYER_FROM_CONTEXT, SETTING_LIVE_DEFAULT_PLAYER_FROM_LIBRARY, SETTING_LIVE_DEFAULT_PLAYER, SETTING_LIVE_LIBRARY_FOLDER

def play_channel(channel, program, language, mode):
    # Get players to use
    if mode == 'select':
        play_plugin = ADDON_SELECTOR.id
    elif mode == 'context':
        play_plugin = plugin.get_setting(SETTING_LIVE_DEFAULT_PLAYER_FROM_CONTEXT)
    elif mode == 'library':
        play_plugin = plugin.get_setting(SETTING_LIVE_DEFAULT_PLAYER_FROM_LIBRARY)
    elif mode == 'default':
        play_plugin = plugin.get_setting(SETTING_LIVE_DEFAULT_PLAYER)
    else:
        play_plugin = mode
    players = active_players("live", filters = {"channel": channel})
    players = [p for p in players if p.id == play_plugin] or players
    if not players:
        xbmc.executebuiltin( "Action(Info)")
        action_cancel()
        return

    # Get parameters
    params = {}
    for lang in get_needed_langs(players):
        params[lang] = get_channel_parameters(channel, program, language)
        params[lang] = to_unicode(params[lang])

    # Go for it
    link = on_play_video(mode, players, params)
    if link:
        action_play({
            'label': channel,
            'path': link,
            'is_playable': True,
            'info_type': 'video',
        })

def get_channel_parameters(channel, program, language):
    channel_regex = re.compile("(.+?)\s*(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*.*?(\d*)$",
                               re.IGNORECASE|re.UNICODE)
    parameters = {}
    parameters['name'] = channel
    parameters['urlname'] = urllib.quote(parameters['name'])
    parameters['shortname'] = parameters['name'][1:-1]
    parameters['basename'] = re.sub(channel_regex, r"\1",channel)
    parameters['shortbasename'] = parameters['basename'][1:-1]
    parameters['extension'] = re.sub(channel_regex, r"\2",channel)
    parameters['delay'] = re.sub(channel_regex, r"\3", channel)
    parameters['program'] = program
    parameters['language'] = language

    return parameters
