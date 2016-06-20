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

import xbmc, xbmcaddon, os
import dixie
import login

AddonID          =  'script.tvportal'
ADDON            =  xbmcaddon.Addon(id=AddonID)
showSFchannels   =  ADDON.getSetting('showSFchannels')
USERDATA         =  xbmc.translatePath(os.path.join('special://home/userdata',''))
ADDON_DATA       =  xbmc.translatePath(os.path.join(USERDATA,'addon_data'))
ADDONS           =  xbmc.translatePath('special://home/addons')
cookies          =  os.path.join(ADDON_DATA,AddonID,'cookies')       

xbmc.executebuiltin("ActivateWindow(busydialog)")

#if __name__ == '__main__':
if not os.path.exists(os.path.join(ADDON_DATA,AddonID)):
    dixie.log("New addon_data folder created")
    os.makedirs(os.path.join(ADDON_DATA,AddonID))
else:
    dixie.log("addon_data already exists")

if not os.path.exists(cookies):
    os.makedirs(cookies)

xbmc.executebuiltin('RunScript(special://home/addons/script.tvportal/createDB.py,normal)')
login.o000O0o()
