# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Revved Up Addon by Deezel
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube addon
#
# Author: deezel
#------------------------------------------------------------

import os
import sys
import plugintools
import xbmc,xbmcaddon
from addon.common.addon import Addon

addonID = 'plugin.video.revvedup'
addon = Addon(addonID, sys.argv)
local = xbmcaddon.Addon(id=addonID)
icon = local.getAddonInfo('icon')

YOUTUBE_CHANNEL_ID_1 = "PLtc57NTUizP538OlT9gAhMhOTv1v5BB4m"
YOUTUBE_CHANNEL_ID_2 = "PLtc57NTUizP7vaa6ui8VV5OIaC1NiDeA9"
YOUTUBE_CHANNEL_ID_3 = "PLtc57NTUizP74wLTCM2A6vyav8hQtsQwJ"
YOUTUBE_CHANNEL_ID_4 = "PLtc57NTUizP4ZpodtQYk8EWqP7m-AaPiG"
YOUTUBE_CHANNEL_ID_5 = "PLtc57NTUizP7uX1ijGsy4_UkbcTWM-kVr"

# Entry point
def run():
    plugintools.log("docu.run")
    
    # Get params
    params = plugintools.get_params()
    
    if params.get("action") is None:
        main_list(params)
    else:
        action = params.get("action")
        exec action+"(params)"
    
    plugintools.close_item_list()

# Main menu
def main_list(params):
    plugintools.log("docu.main_list "+repr(params))

    plugintools.add_item( 
        #action="", 
        title="Live Events -- Coming Soon",
        url="",
        thumbnail="https://i.ytimg.com/vi/5AAagPtRTY8/hqdefault.jpg?custom=true&w=196&h=110&stc=true&jpg444=true&jpgq=90&sp=68&sigh=pIhFUvyUFOgbEQmq-01X2fpH6_Q",
        folder=True )

    plugintools.add_item( 
        #action="", 
        title="Nascar replays 2016",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_1+"/",
        thumbnail="http://i1.ytimg.com/vi/yj__WIAAWG8/hqdefault.jpg",
        folder=True )

    plugintools.add_item( 
        #action="", 
        title="Tech Talk",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_2+"/",
        thumbnail="https://i.ytimg.com/vi/kxDFlJIwKzY/hqdefault.jpg?custom=true&w=196&h=110&stc=true&jpg444=true&jpgq=90&sp=68&sigh=-049rfdbLDq75mJqkOlRFuWYp34",
        folder=True )

    plugintools.add_item( 
        #action="", 
        title="Spectacular Wrecks",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_3+"/",
        thumbnail="https://i.ytimg.com/vi/84hz9w2GlV4/hqdefault.jpg?custom=true&w=320&h=180&stc=true&jpg444=true&jpgq=90&sp=68&sigh=hxhObi9FHZUKZg-JI4pOgKibK6w",
        folder=True )

    plugintools.add_item( 
        #action="", 
        title="Sprint Cup Recap",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_4+"/",
        thumbnail="https://i.ytimg.com/vi/-bNhcVc8UPE/hqdefault.jpg?custom=true&w=320&h=180&stc=true&jpg444=true&jpgq=90&sp=68&sigh=RSQOEvCNxgwRHd_ed4-gNm02nwE",
        folder=True )

    plugintools.add_item( 
        #action="", 
        title="Xfinity Recap",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_5+"/",
        thumbnail="https://i.ytimg.com/vi/LHyuUABChEw/hqdefault.jpg?custom=true&w=320&h=180&stc=true&jpg444=true&jpgq=90&sp=68&sigh=iqsiIV3dCmhVyt2A3o2N5nc8--w",
        folder=True )

run()
