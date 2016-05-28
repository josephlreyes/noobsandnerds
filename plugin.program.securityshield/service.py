import xbmc, xbmcaddon
from datetime import datetime,timedelta
#################################################
AddonID        = 'plugin.program.securityshield'
#################################################
ADDON            =  xbmcaddon.Addon(id=AddonID)
runservice       =  ADDON.getSetting('runservice')
feqservice       =  ADDON.getSetting('feqservice')
lastservice      =  ADDON.getSetting('lastservice')
last             =  datetime.strptime(lastservice, '%Y-%m-%d %H:%M:%S.%f')
now              =  datetime.now()

def runService():
	xbmc.executebuiltin('XBMC.RunScript(special://home/addons/'+AddonID+'/default.py,silent)')
	ADDON.setSetting('lastservice', str(now))

if runservice == 'true':
	run = False
	if feqservice == '0':   run = True
	elif feqservice == '1': run = True if now > last + timedelta(days=1) else False
	elif feqservice == '2': run = True if now > last + timedelta(days=3) else False
	elif feqservice == '3': run = True if now > last + timedelta(days=7) else False
	
	if run: runService()