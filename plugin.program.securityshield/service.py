import xbmc, xbmcaddon
#################################################
AddonID        = 'plugin.program.securityshield'
#################################################
ADDON            =  xbmcaddon.Addon(id=AddonID)
runservice       =  ADDON.getSetting('runservice')

if runservice == 'true':
    xbmc.executebuiltin('XBMC.RunScript(special://home/addons/'+AddonID+'/default.py,silent)')
    xbmc.executebuiltin('XBMC.AlarmClock(securitycheck,XBMC.RunScript(special://home/addons/'+AddonID+'/default.py,silent),23:59:59,silent,loop)')