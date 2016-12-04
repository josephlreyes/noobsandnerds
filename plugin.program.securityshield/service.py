import xbmc
import xbmcaddon
#################################################
AddonID        = 'plugin.program.securityshield'
#################################################
ADDON            =  xbmcaddon.Addon(id=AddonID)
runservice       =  ADDON.getSetting('runservice')
feqservice       =  ADDON.getSetting('feqservice')
lastservice      =  ADDON.getSetting('lastservice')
##########################################################################################
def Timestamp():
    import time
    now = time.time()
    localtime = time.localtime(now)
    return time.strftime('%Y%m%d%H%M%S', localtime)
##########################################################################################
def runService():
	xbmc.executebuiltin('XBMC.RunScript(special://home/addons/'+AddonID+'/default.py,silent)')
	ADDON.setSetting('lastservice', now)
##########################################################################################
now = str(Timestamp())
if runservice == 'true':
	run = False
	try:
		lastservice = int(lastservice)
	except:
		lastservice = 0

	xbmc.log('### Last scan: %s' % lastservice)
	if feqservice == '0':   run = True
	elif feqservice == '1': run = True if Timestamp() > (lastservice + 86400) else False 	# 1 day
	elif feqservice == '2': run = True if Timestamp() > (lastservice + 259200) else False	# 3 days
	elif feqservice == '3': run = True if Timestamp() > (lastservice + 604800) else False	# 7 days
	
	if run: runService()