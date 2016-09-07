#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import xbmc, xbmcvfs
import re
pluginid = "plugin.video.metalliq"

def get_url(stream_file):
    if stream_file.endswith(".strm"):
        f = xbmcvfs.File(stream_file)
        try:
            content = f.read()
            if content.startswith("plugin://" + pluginid):
                return content.replace("/library", "/context")
        finally: f.close()
    return None

def main():
    stream_file = xbmc.getInfoLabel('ListItem.FileNameAndPath')
    url = get_url(stream_file)
    if url is None:
        if xbmc.getInfoLabel('ListItem.Title') and xbmc.getInfoLabel('ListItem.IMDBNumber'): url = "plugin://{0}/movies/play/imdb/{1}/context".format(pluginid, xbmc.getInfoLabel('ListItem.IMDBNumber'))
        elif xbmc.getInfoLabel('ListItem.Title') and not xbmc.getInfoLabel('ListItem.IMDBNumber'): url = "plugin://{0}/movies/play_by_name/{1}/en".format(pluginid, xbmc.getInfoLabel('ListItem.Title'))
        elif xbmc.getInfoLabel('ListItem.TVShowTitle') and xbmc.getInfoLabel('ListItem.IMDBNumber') and xbmc.getInfoLabel('ListItem.Season') and xbmc.getInfoLabel('ListItem.Episode'): url = "plugin://{0}/tv/play/{1}/{2}/{3}/context".format(pluginid, xbmc.getInfoLabel('ListItem.IMDBNumber'), xbmc.getInfoLabel('ListItem.Season'), xbmc.getInfoLabel('ListItem.Episode'))
        elif xbmc.getInfoLabel('ListItem.TVShowTitle') and xbmc.getInfoLabel('ListItem.IMDBNumber') and xbmc.getInfoLabel('ListItem.Season'): url = "plugin://{0}/tv/play/{1}/{2}/1/context".format(pluginid, xbmc.getInfoLabel('ListItem.IMDBNumber'), xbmc.getInfoLabel('ListItem.Season'))
        elif xbmc.getInfoLabel('ListItem.TVShowTitle') and xbmc.getInfoLabel('ListItem.IMDBNumber'): url = "plugin://{0}/tv/play/{1}/1/1/context".format(pluginid, xbmc.getInfoLabel('ListItem.IMDBNumber'))
        elif xbmc.getInfoLabel('ListItem.TVShowTitle'): url = "plugin://{0}/tv/play_by_name_only/{1}/<lang>".format(pluginid, xbmc.getInfoLabel('ListItem.TVShowTitle'))
        elif xbmc.getInfoLabel('ListItem.Label'): return xbmc.executebuiltin("RunPlugin(plugin://{0}/play/{1})".format(pluginid, re.sub(r'\[[^)].*?\]', '', xbmc.getInfoLabel('ListItem.Label'))))
        else: url = None
        if url is None:
            title = "[COLOR ff0084ff]M[/COLOR]etalli[COLOR ff0084ff]Q[/COLOR]"
            msg = "Invalid media file. Try using the [COLOR ff0084ff]M[/COLOR]etalli[COLOR ff0084ff]Q[/COLOR]-Context-Menu addon instead"
            xbmc.executebuiltin('XBMC.Notification("%s", "%s", "%s", "%s")' % (msg, title, 2000, ''))
            return
        xbmc.executebuiltin("RunPlugin({0})".format(url))
    else:
        xbmc.executebuiltin("PlayMedia({0})".format(url))
    
if __name__ == '__main__':
    main()