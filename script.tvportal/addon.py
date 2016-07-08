#
#      Copyright (C) 2016 noobsandnerds.com
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#

import xbmc, xbmcaddon, xbmcgui, os
import dixie, shutil

AddonID          =  'script.tvportal'
ADDON            =  xbmcaddon.Addon(id=AddonID)
showSFchannels   =  ADDON.getSetting('showSFchannels')
usenanchan       =  ADDON.getSetting('usenanchan')
usenancats       =  ADDON.getSetting('usenancats')
USERDATA         =  xbmc.translatePath(os.path.join('special://home/userdata',''))
ADDON_DATA       =  xbmc.translatePath(os.path.join(USERDATA,'addon_data'))
ADDONS           =  xbmc.translatePath('special://home/addons')
resources        =  dixie.RESOURCES
cookies          =  os.path.join(ADDON_DATA,AddonID,'cookies')       
datapath         =  dixie.PROFILE
extras           =  os.path.join(datapath,   'extras')
logopack_none    =  os.path.join(extras,'logos','None')
logopack_colour  =  os.path.join(extras,'logos','Colour Logo Pack')
channel_xml      =  os.path.join(resources,  'chan.xml')
xmlmaster        =  os.path.join(resources,  'chan.xml')
catsmaster       =  os.path.join(resources,  'cats.xml')
chanxml          =  os.path.join(datapath,   'chan.xml')
catsxml          =  os.path.join(datapath,   'cats.xml')
dialog           =  xbmcgui.Dialog()
cont             =  0

if not os.path.exists(os.path.join(ADDON_DATA,AddonID)):
    dixie.log("New addon_data folder created")
    os.makedirs(os.path.join(ADDON_DATA,AddonID))
else:
    dixie.log("addon_data already exists")

if not os.path.exists(cookies):
    os.makedirs(cookies)

if not os.path.exists(logopack_none):
    os.makedirs(logopack_none)

if not os.path.exists(logopack_colour):
    os.makedirs(logopack_colour)

if not os.path.exists(chanxml) and usenanchan == 'true':
    dixie.log("Copying chan.xml to addon_data")
    shutil.copyfile(xmlmaster, chanxml)
else:
    dixie.log("Chan.xml file already exists in addon_data")

if not os.path.exists(catsxml) and usenancats == 'true':
    dixie.log("Copying cats.xml to addon_data")
    shutil.copyfile(catsmaster, catsxml)
else:
    dixie.log("Cats.xml file exists in addon_data")

try:
    import login
    cont = 1
    xbmc.executebuiltin("ActivateWindow(busydialog)")
except:
    xbmc.executebuiltin('ActivateWindow(Programs,addons://sources/executable)')
    xbmc.executebuiltin("Container.SetViewMode(50)")
    xbmc.sleep(2000)
    temparray  = []
    listcount  = xbmc.getInfoLabel('Container(id).NumItems')
    listcount = int(listcount)+1
    counter    = 0
    while counter < listcount:
        addonname = xbmc.getInfoLabel('Container(id).ListItem(%s).Label'%counter)
        temparray.append([counter,addonname])
        xbmc.log('Addon name: %s | %s'%(addonname,counter))
        counter += 1
    for item in temparray:
        if item[1] == 'TV Portal':
            pos = item[0]
            cont = 1
    xbmc.executebuiltin('Control.Move(50,%s)'%pos)
    xbmc.sleep(1000)
    if cont:
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        import login

if cont:
    xbmc.executebuiltin('RunScript(special://home/addons/script.tvportal/createDB.py,normal)')
    login.Ii11Ii1I()
