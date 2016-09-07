#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon

ADDON = xbmcaddon.Addon()

def main():
    url = "plugin://{0}/toggle/{1}".format(ADDON.getAddonInfo('id'), ADDON.getSetting("preferred_toggle"))
    xbmc.executebuiltin("RunPlugin({0})".format(url))

if __name__ == '__main__':
    main()