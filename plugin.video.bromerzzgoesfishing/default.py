# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Bromerzz Goes Fishing Addon by bromerzz
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube addon
#
# Author: bromerzz
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
BASE  = "plugin://plugin.video.youtube/playlist/"
BASE2 = "plugin://plugin.video.youtube/channel/"

# Set each of your YouTube playlist id's
YOUTUBE_CHANNEL_ID_1 = "PLRjomIk8urmEj_1boB4qG-sJfLLfbJqq2"
YOUTUBE_CHANNEL_ID_2 = "PLnDj4GODT_QpaemQB4395I9wRwCnZvx6x"
YOUTUBE_CHANNEL_ID_3 = "PLfb8E7lARImvzrAq0O6jyQcstw7aKZvLq"
YOUTUBE_CHANNEL_ID_4 = "PLlJDPmb6OexrDnAFNBNJez8zRe4EECDZY"
YOUTUBE_CHANNEL_ID_5 = "UCBDT-Kl4nHgEvpwYfLb315w"

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
    my_message= "{'title' : 'Support & Suggestions', 'msg' : \"If you come across any online content you'd like to get added please use the support thread at noobsandnerds.com and I'll be happy to look into it for you.\"}"

    Add_Dir(
        name="Support/Suggestions", url=my_message, mode="simple_dialog", folder=False,
        icon="https://cdn2.iconfinder.com/data/icons/picons-basic-2/57/basic2-087_info-512.png")
        
    Add_Dir( 
        name="Popular Fly Fishing Videos", url=BASE+YOUTUBE_CHANNEL_ID_1+"/", folder=True,
        icon="http://www.free-icons-download.net/images/fishing-icons-23810.png")

    Add_Dir( 
        name="Fly TV", url=BASE+YOUTUBE_CHANNEL_ID_2+"/", folder=True,
        icon="https://yt3.ggpht.com/-ldvmtOEepRk/AAAAAAAAAAI/AAAAAAAAAAA/OOEsBMgcqQI/s100-c-k-no-mo-rj-c0xffffff/photo.jpg")

    Add_Dir( 
        name="Fishing videos from DALLMYD", url=BASE+YOUTUBE_CHANNEL_ID_3+"/", folder=True,
        icon="https://yt3.ggpht.com/-HB9PwSeNSE8/AAAAAAAAAAI/AAAAAAAAAAA/LmADXY0mgbA/s100-c-k-no-mo-rj-c0xffffff/photo.jpg")

    Add_Dir( 
        name="Sea Fishing videos from TAFishing", url=BASE+YOUTUBE_CHANNEL_ID_4+"/", folder=True,
        icon="https://yt3.ggpht.com/-P2USlMtGNXo/AAAAAAAAAAI/AAAAAAAAAAA/sDV3FPYrotM/s100-c-k-no-mo-rj-c0xffffff/photo.jpg")

    Add_Dir( 
        name="Uncut Angling Channel", url=BASE2+YOUTUBE_CHANNEL_ID_5+"/", folder=True,
        icon="https://yt3.ggpht.com/-8Rt7LjDZrtU/AAAAAAAAAAI/AAAAAAAAAAA/-0-9PLOJWXM/s100-c-k-no-mo-rj-c0xffffff/photo.jpg")

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