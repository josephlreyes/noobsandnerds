# -*- coding: utf-8 -*-

"""
    Bob Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import login

ADDON_ID    = 'plugin.video.bob'
HOME        = xbmc.translatePath('special://home')
ADDON_DATA  = xbmc.translatePath('special://profile/addon_data')
ADDONS      = os.path.join(HOME,'addons')
BOB_DATA    = os.path.join(ADDON_DATA,ADDON_ID)
BOB_COOKIE  = os.path.join(BOB_DATA,'cookies')

if 'credits' in sys.argv[0]:
    try:
        f = xbmcvfs.File('special://home/addons/plugin.video.bob/credits.txt')
        text = f.read() ; f.close()
        if xbmc.getInfoLabel('System.ProfileName') != "Master user":
            you = xbmc.getInfoLabel('System.ProfileName')
        elif xbmc.getCondVisibility('System.Platform.Windows') == True or xbmc.getCondVisibility('System.Platform.OSX') == True:
            if "Users\\" in HOME:
                proyou = str(HOME).split("Users\\")
                preyou = str(proyou[1]).split("\\")
                you = preyou[0]
            else: you = "You"
        else: you = "You"
        if you: newcredits = text + "\r\n\r\n\r\nSpecial thanks to:\r\n\r\n" + you + " for trying our new addon.\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\nDo not be alarmed. \r\nNo personal data was gathered or stored in anyway.\r\nWe just used kodi's profile name or your OSX/Windows user-foldername to personalize this message on the fly..."
        label = '%s - %s' % (xbmc.getLocalizedString(470), xbmcaddon.Addon().getAddonInfo('name'))
        id = 10147
        xbmc.executebuiltin('ActivateWindow(%d)' % id)
        xbmc.sleep(100)
        win = xbmcgui.Window(id)
        retry = 50
        while (retry > 0):
            try:
                xbmc.sleep(10)
                win.getControl(1).setLabel(label)
                win.getControl(5).setText(newcredits)
                retry = 0
            except:
                retry -= 1
    except:
        pass

if not os.path.exists(BOB_DATA):
    os.makedirs(BOB_DATA)
    try:
        f = xbmcvfs.File(xbmcaddon.Addon().getAddonInfo('changelog'))
        text = f.read(); f.close()
        label = '%s - %s' % (xbmc.getLocalizedString(24054), xbmcaddon.Addon().getAddonInfo('name'))
        id = 10147
        xbmc.executebuiltin('ActivateWindow(%d)' % id)
        xbmc.sleep(100)
        win = xbmcgui.Window(id)
        retry = 50
        while (retry > 0):
            try:
                xbmc.sleep(10)
                win.getControl(1).setLabel(label)
                win.getControl(5).setText(text)
                retry = 0
            except: retry -= 1
    except: pass

if not os.path.exists(BOB_COOKIE):
    os.makedirs(BOB_COOKIE)

login.IIIIii()