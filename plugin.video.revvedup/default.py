# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Revved Up Addon by Deezel
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube addon
#
# Author: deezel
#------------------------------------------------------------

import os           # access operating system commands
import urlparse     # splits up the directory path - much easier importing this than coding it up ourselves
import xbmc         # the base xbmc functions, pretty much every add-on is going to need at least one function from here
import xbmcaddon    # pull addon specific information such as settings, id, fanart etc.
import xbmcgui      # gui based functions, contains things like creating dialog pop-up windows
import xbmcplugin   # contains functions required for creating directory structure style add-ons (plugins)

import koding       # (*) a framework for easy add-on development, this template is to be used in conjunction with this module.

from koding import Add_Dir  # By importing something like this we don't need to use <module>.<function> to call it,
                            # instead you can just use the function name - in this case Add_Dir().

addon_id     = xbmcaddon.Addon().getAddonInfo('id')
dialog       = xbmcgui.Dialog()

# Set the base plugin url you want to hook into
BASE = "plugin://plugin.video.youtube/playlist/"

# Set each of your YouTube playlist id's
YOUTUBE_CHANNEL_ID_1 = "PLtc57NTUizP538OlT9gAhMhOTv1v5BB4m"
YOUTUBE_CHANNEL_ID_2 = "PLtc57NTUizP7vaa6ui8VV5OIaC1NiDeA9"
YOUTUBE_CHANNEL_ID_3 = "PLtc57NTUizP74wLTCM2A6vyav8hQtsQwJ"
YOUTUBE_CHANNEL_ID_4 = "PLtc57NTUizP4ZpodtQYk8EWqP7m-AaPiG"
YOUTUBE_CHANNEL_ID_5 = "PLtc57NTUizP7uX1ijGsy4_UkbcTWM-kVr"
YOUTUBE_CHANNEL_ID_6 = "PLtc57NTUizP4FFPP6c_Xkp8NDvjhIw3Rj"



master_modes = {
# Required for certain koding functions to work
    "play_video"    : "koding.Play_Video(url)",
    "show_tutorial" : "koding.Show_Tutorial(url)",
    "tutorials"     : "koding.Grab_Tutorials()",
# Our custom functions created in this file
    "simple_dialog" : "Simple_Dialog(url)",
}

def Main_Menu():
# Uncomment the following line for help creating your add-on
    # Add_Dir(name='KODING TUTORIALS', url='', mode='tutorials', folder=True, icon=os.path.join(art_path,'icon.png'), fanart=os.path.join(art_path,'fanart.jpg'))
    
# An example title/message we're going to send through to a popup dialog in the first Add_Dir item
    my_message= "{'title' : 'LIVE EVENTS', 'msg' : 'This section is a work in progress, please keep an eye on the forum at noobsandnerds.com for all the latest updates'}"

    Add_Dir(
        name="Live Events -- Coming Soon", url=my_message, mode="simple_dialog", folder=False,
        icon="https://i.ytimg.com/vi/5AAagPtRTY8/hqdefault.jpg?custom=true&w=196&h=110&stc=true&jpg444=true&jpgq=90&sp=68&sigh=pIhFUvyUFOgbEQmq-01X2fpH6_Q")
		
    Add_Dir( 
        name="Nascar replays 2017", url=BASE+YOUTUBE_CHANNEL_ID_6+"/", folder=True,
        icon="https://i.ytimg.com/vi/80IBoKOWU-Q/hqdefault.jpg?custom=true&w=168&h=94&stc=true&jpg444=true&jpgq=90&sp=67&sigh=g5B0Gy5cGfz4go-6nvvId3dYq1U")		

    Add_Dir( 
        name="Nascar replays 2016", url=BASE+YOUTUBE_CHANNEL_ID_1+"/", folder=True,
        icon="http://i1.ytimg.com/vi/yj__WIAAWG8/hqdefault.jpg")

    Add_Dir( 
        name="Tech Talk", url=BASE+YOUTUBE_CHANNEL_ID_2+"/", folder=True,
        icon="https://i.ytimg.com/vi/kxDFlJIwKzY/hqdefault.jpg?custom=true&w=196&h=110&stc=true&jpg444=true&jpgq=90&sp=68&sigh=-049rfdbLDq75mJqkOlRFuWYp34")

    Add_Dir( 
        name="Spectacular Wrecks", url=BASE+YOUTUBE_CHANNEL_ID_3+"/", folder=True,
        icon="https://i.ytimg.com/vi/84hz9w2GlV4/hqdefault.jpg?custom=true&w=320&h=180&stc=true&jpg444=true&jpgq=90&sp=68&sigh=hxhObi9FHZUKZg-JI4pOgKibK6w")

    Add_Dir( 
        name="Sprint Cup Recap", url=BASE+YOUTUBE_CHANNEL_ID_4+"/", folder=True,
        icon="https://i.ytimg.com/vi/-bNhcVc8UPE/hqdefault.jpg?custom=true&w=320&h=180&stc=true&jpg444=true&jpgq=90&sp=68&sigh=RSQOEvCNxgwRHd_ed4-gNm02nwE")

    Add_Dir( 
        name="Xfinity Recap", url=BASE+YOUTUBE_CHANNEL_ID_5+"/",folder=True,
        icon="https://i.ytimg.com/vi/LHyuUABChEw/hqdefault.jpg?custom=true&w=320&h=180&stc=true&jpg444=true&jpgq=90&sp=68&sigh=iqsiIV3dCmhVyt2A3o2N5nc8--w")


def Simple_Dialog(my_vars):
    my_vars = eval(my_vars)
    title   = my_vars['title']
    message = my_vars['msg']
    dialog.ok(title, message)
#----------------------------------------------------------------

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?', '')))

try: name           = params["name"]
except: name        = ''

try: description    = params["description"]
except: description = name

try: fanart         = params["fanart"]
except: fanart      = ''

try: iconimage      = params["iconimage"]
except: iconimage   = ''

try: mode           = params["mode"]
except: mode        = None

try: url            = params["url"]
except: url         = ''

if mode in master_modes:
    try:
        eval(master_modes[mode])
    except:
        koding.Text_Box('ERROR IN CODE',koding.Last_Error())
elif mode == None:
    Main_Menu()
else:
    dialog.ok('MODE DOES NOT EXIST','The following mode does not exist in your master_modes dictionary:','[COLOR=dodgerblue]%s[/COLOR]'%mode)

xbmcplugin.endOfDirectory(int(sys.argv[1]))