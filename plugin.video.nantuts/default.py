# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Noobs Addon by coldkeys
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube addon
#
# Author: coldkeys
#------------------------------------------------------------

import os
import sys
import plugintools
import xbmc,xbmcaddon
from addon.common.addon import Addon

addonID = 'plugin.video.nantuts'
addon = Addon(addonID, sys.argv)
local = xbmcaddon.Addon(id=addonID)
icon = local.getAddonInfo('icon')

YOUTUBE_CHANNEL_ID_1  = "PL-IP2f4fsmZWb6QXnMUxqUFKGK5Q8ekfP"
YOUTUBE_CHANNEL_ID_2  = "PL-IP2f4fsmZVj1nP-VFpHwlafCDUPinSA"
YOUTUBE_CHANNEL_ID_3  = "PL-IP2f4fsmZVz1Hi01EqftbF5G2xqajyW"
YOUTUBE_CHANNEL_ID_4  = "PL-IP2f4fsmZVHQRPqxkky8mQZFlYkNmsT"
YOUTUBE_CHANNEL_ID_5  = "PL-IP2f4fsmZVdHubOX9-MkXnF23qBB_yY"
YOUTUBE_CHANNEL_ID_6  = "PLyEyQCZKWQANWp2WIhxOUp9rkmPVIvg6l"
YOUTUBE_CHANNEL_ID_7  = "PLyEyQCZKWQAMxYghl1Vtv8D4qUN4bqo-5"
YOUTUBE_CHANNEL_ID_8  = "PLyEyQCZKWQAMXVPhetl505wZIqStq439a"
YOUTUBE_CHANNEL_ID_9  = "PL-IP2f4fsmZWdB9jPbNUUmql8LTYrQvGz"
YOUTUBE_CHANNEL_ID_10 = "PL-IP2f4fsmZXnlZMHPyGkUsiNPPygbEj1"
YOUTUBE_CHANNEL_ID_11 = "PL-IP2f4fsmZX6RzTdM0AdcRzmwoJ9lWXY"
YOUTUBE_CHANNEL_ID_12 = "PL-IP2f4fsmZX9Sug-yU92V7sZEdFlxhcs"
YOUTUBE_CHANNEL_ID_13 = "PL-IP2f4fsmZU_gBqV2wbH5_puqK8krvPG"
YOUTUBE_CHANNEL_ID_14 = "PL-IP2f4fsmZUDfJOOZzRNBynhAZH5-dYc"
YOUTUBE_CHANNEL_ID_15 = "PL-IP2f4fsmZWw72ldIbtj6id4_TWtHfm3"


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
        title="TV Portal Guides",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_1+"/",
        thumbnail="https://i.ytimg.com/vi/WdKIzajiBBI/mqdefault.jpg",
        folder=True )

    plugintools.add_item( 
        #action="", 
        title="Python Koding",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_2+"/",
        thumbnail="https://i.ytimg.com/vi/70PgivqjWC0/mqdefault.jpg",
        folder=True )
    
    plugintools.add_item( 
        #action="", 
        title="Kodi Addons",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_3+"/",
        thumbnail="https://i.ytimg.com/vi/HsiXVi-sKxA/mqdefault.jpg",
        folder=True )
    
    plugintools.add_item( 
        #action="", 
        title="Kodi Basics",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_4+"/",
        thumbnail="https://i.ytimg.com/vi/WdKIzajiBBI/mqdefault.jpg",
        folder=True )

    plugintools.add_item( 
        #action="", 
        title="Kodi Library FAQs",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_5+"/",
        thumbnail="http://arbbuilds.org/Tutpics/Untitled44.jpg",
        folder=True )
    
    plugintools.add_item( 
        #action="", 
        title="Kodi Matters",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_6+"/",
        thumbnail="https://i.ytimg.com/vi/je_PaqCr5JI/mqdefault.jpg",
        folder=True )

    plugintools.add_item( 
        #action="", 
        title="DaButcher Digs Deeper",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_7+"/",
        thumbnail="http://arbbuilds.org/Tutpics/IMG_20160906_203447.jpg",
        folder=True )
    
    plugintools.add_item( 
        #action="", 
        title="Kodi 101",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_8+"/",
        thumbnail="http://arbbuilds.org/Tutpics/Untitled36.jpg",
        folder=True )

    plugintools.add_item( 
        #action="", 
        title="OpenELEC Specific",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_9+"/",
        thumbnail="http://arbbuilds.org/Tutpics/Untitled43.jpg",
        folder=True )
    
    plugintools.add_item( 
        #action="", 
        title="Hardware: PC (Windows)",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_10+"/",
        thumbnail="http://arbbuilds.org/Tutpics/Untitled42.jpg",
        folder=True )

    plugintools.add_item( 
        #action="", 
        title="Hardware: PC (Linux)",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_11+"/",
        thumbnail="http://arbbuilds.org/Tutpics/Untitled41.jpg",
        folder=True )

    plugintools.add_item( 
        #action="", 
        title="Hardware: (Android)",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_12+"/",
        thumbnail="http://arbbuilds.org/Tutpics/Untitled40.jpg",
        folder=True )
    
    plugintools.add_item( 
        #action="", 
        title="Hardware: (Raspberry Pi)",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_13+"/",
        thumbnail="http://arbbuilds.org/Tutpics/Untitled39.jpg",
        folder=True )

    plugintools.add_item( 
        #action="", 
        title="Hardware: (Xbox)",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_14+"/",
        thumbnail="http://arbbuilds.org/Tutpics/Untitled38.jpg",
        folder=True )
    
    plugintools.add_item( 
        #action="", 
        title="TLBB (2016 Venztech units)",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID_15+"/",
        thumbnail="http://arbbuilds.org/Tutpics/Untitled37.jpg",
        folder=True )         
run()
