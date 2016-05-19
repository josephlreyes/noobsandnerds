# Security Check - Check for outdated content installed on system
# Copyright (C) 2016 Lee Randall (whufclee)
#

#  I M P O R T A N T :

#  You are free to use this code under the rules set out in the license below.
#  However under NO circumstances should you remove this license!

#  GPL:
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
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html

# Global imports
import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon
import os, sys, shutil, zipfile, time

######################################################
AddonID='plugin.program.securityshield'
AddonName='Security Shield'
######################################################
ADDON           =  xbmcaddon.Addon(id=AddonID)
dialog          =  xbmcgui.Dialog()
dp              =  xbmcgui.DialogProgress()
HOME            =  xbmc.translatePath('special://home')
PROFILE         =  xbmc.translatePath('special://profile')
ADDON_DATA      =  os.path.join(PROFILE,'addon_data')
ADDONS          =  os.path.join(HOME,'addons')
quarantine_path =  os.path.join(HOME,'quarantine')
mainfanart      =  os.path.join(ADDONS,AddonID,'Fanart.jpg')
artpath         =  os.path.join(ADDONS,AddonID,'resources')
packages        =  os.path.join(ADDONS,'packages')
temp			=  xbmc.translatePath('special://temp')
cookies			=  os.path.join(temp,'cookies.dat')
reloadprofile   =  0
# Create arrays for our final results
versionupdate   =   []
blocked         =   []
confirmed       =   []
unconfirmed     =   []
unknown         =   []
existing        =   []
q_list          =   []
##########################################################################################
# Grab a list of all the content instsalled in our Kodi addons folder
def grab_installed():
    locallist = []
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    for name in os.listdir(ADDONS):
# copy all the repo's to repopath folder in userdata and zip up with version number
        if not 'packages' in name and not 'cygpfi' in name:
            currentpath =   os.path.join(ADDONS,name)
            currentfile =   os.path.join(currentpath,'addon.xml')
            
            if os.path.exists(currentfile):
                readfile    = open(currentfile, mode='r')
                content     = readfile.read()
                readfile.close()

# find version number, there are 2 version tags in the addon.xml, we need the second one.
                localmatch          = re.compile('<addon[\s\S]*?">').findall(content)
                localcontentmatch   = localmatch[0] if (len(localmatch) > 0) else 'None'
                localversion        = re.compile('version="(.+?)"').findall(localcontentmatch)
                localversionmatch   = localversion[0] if (len(localversion) > 0) else '0'

# pull the name and id of add-on
                idmatch     = re.compile('id="(.+?)"').findall(localcontentmatch)
                addonid     = idmatch[0] if (len(idmatch) > 0) else ''
                namematch   = re.compile(' name="(.+?)"').findall(localcontentmatch)
                addonname   = namematch[0] if (len(namematch) > 0) else addonid

# Add to the array of locally installed add-ons
                locallist.append([addonid,localversionmatch,addonname,currentpath])
                srcomments = 'Although we\'re fairly certain the author of SR meant no harm and was only trying to help the community there is a huge flaw in the way it works. Efforts have been made to improve the system but there are still some issues. Content is re-uploaded and has conflicted with the original developers versions on a number of occasions. This has resulted in certain addons breaking because the version number on SR is wrong (and higher) than the official version, so even though if you install from the real developers repo but you have SR installed you may still encounter problems trying to get the real version installed.'
                if 'superrepo' in addonid:
                    blocked.append([name,addonid,localversionmatch,srcomments,currentpath])
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    return locallist
##########################################################################################
# Create a standard text box
def Text_Boxes(heading,anounce):
  class TextBox():
    WINDOW=10147
    CONTROL_LABEL=1
    CONTROL_TEXTBOX=5
    def __init__(self,*args,**kwargs):
      xbmc.executebuiltin("ActivateWindow(%d)" % (self.WINDOW, )) # activate the text viewer window
      self.win=xbmcgui.Window(self.WINDOW) # get window
      xbmc.sleep(500) # give window time to initialize
      self.setControls()
    def setControls(self):
      self.win.getControl(self.CONTROL_LABEL).setLabel(heading) # set heading
      try:
        f=open(anounce); text=f.read()
      except:
        text=anounce
      self.win.getControl(self.CONTROL_TEXTBOX).setText(str(text))
      return
  TextBox()
  while xbmc.getCondVisibility('Window.IsVisible(10147)'):
      xbmc.sleep(500)
##########################################################################################
# Grab contents of a web page
def Open_URL(url, t):
    req = urllib2.Request(url)
    req.add_header('User-Agent' , 'Mozilla/5.0 (Windows; U; Windows NT 10.0; WOW64; Windows NT 5.1; en-GB; rv:1.9.0.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36 Gecko/2008092417 Firefox/3.0.3')
    counter = 0
    success = False
    while counter < 5 and success == False: 
        response    =   urllib2.urlopen(req, timeout = t)
        link        =   response.read()
        response.close()
        counter += 1
        if link != '':
            success = True
    if success == True:
        return link.replace('\r','').replace('\n','').replace('\t','')
    else:
        dialog.ok('Unable to contact server','There was a problem trying to access the server, please try again later.')
        return
##########################################################################################
def check_content(localmaster, onlinemaster):
# Loop through each item in our local array and check against online array
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    for item in localmaster:
        addonid     = item[0]
        version     = item[1]
        name        = item[2]
        path        = item[3]
        for masteritem in onlinemaster:
            found           = 0
            masterid        = masteritem[0]
            masterstatus    = masteritem[1]
            masterversion   = masteritem[2]
            masterrepo      = masteritem[3]
            mastercomments  = masteritem[4]
            if masterid == addonid:
                if masterstatus == 'b':
                    blocked.append([name,addonid,version,mastercomments,path])
                if masterstatus == 'c':
                    confirmed.append([name,addonid,version,mastercomments,path])
                elif masterstatus == 'u':
                    unconfirmed.append([name,addonid,version,mastercomments,path])
                elif version < masterversion:
                    versionupdate.append([name,addonid,version,masterversion,masterrepo,path])
                existing.append(addonid)
        if not addonid in existing:
            unknown.append([name, addonid, version,'No details found on Add-on Portal, please notify the team at noobsandnerds if you\'d like this submitted',path])
    xbmc.executebuiltin("Dialog.Close(busydialog)")

    if len(blocked)>0:
        if len(blocked) == 1:
            dialog.ok(str(len(blocked))+" serious warning", 'There is 1 item on your system that\'s been flagged by the community as being known to cause serious problems on Kodi systems. Please view the following text and press back when finished to choose how to proceed.')
        else:
            dialog.ok(str(len(blocked))+" serious warnings", 'There are '+str(len(blocked))+' items on your system that have been flagged as having known issues which can cause serious problems on Kodi systems. Please view the following list of add-ons affected and then press back and you can decide what to do with them.')
        cleantext = clean_text_box(blocked)
        Text_Boxes('MARKED AS DANGEROUS','The following items have been flagged by the community as dangerous and we highly recommend putting them in quarantine now. The most common reason for this is repositories which re-upload others work which is definitely a severe security risk. '
            'Often they contain hundreds if not thousands of add-ons which the repo host cannot possibly police and generally everything and anything gets added (malicious or not). If you\'ve previously had add-ons showing as updates available in the past but '
            'they refused to update there\'s a very good chance it was one of these repositories causing the issues.[CR][CR][COLOR=dodgerblue]WARNING: [/COLOR]When installing content you should ALWAYS use the official developers repositories, installing from third parties can cause problems and of course whenever you install a repository '
            'you are allowing the maintainer of that repo full access to your system. It doesn\'t take a genius to code up malicious spyware or system crippling viruses on the Kodi system - it is VERY vulnerable so always please be vigilant when searching the web and installing content, only install from trusted sources. It\'s worth noting that you can '
            'install any add-on via Community Portal and nothing is re-uploaded, absolutely everything comes direct from the original developers repositories and the relavant repo is auto-installed so that is certainly one of the safest ways to install content.[CR][CR]' +cleantext+'[CR][CR][COLOR=dodgerblue]'
            'Are you the developer of something listed here?[/COLOR][CR]If you feel something is incorrectly tagged please post on the noobsandnerds forum with any proof you can provide and the team will look into updating the records. The list is compiled from a mixture of community driven reports combined with auto-generated scans on repos and as with any AV program there is a chance of false positives.')
        choice = dialog.yesno('All or Selective','Would you like to automatically quarantine all of these items or would you prefer to choose which ones to remove?',yeslabel='quarantine ALL', nolabel='Select Items')
        if choice:
            quarantine('all',blocked)
        else:
            quarantine('select',blocked)

    if len(confirmed)>0:
        if len(confirmed) == 1:
            dialog.ok(str(len(confirmed))+" confirmed as depreciated", 'There is 1 item on your system that\'s confirmed as broken and is not going to be updated. Please view the following text and then press back - you can then decide what to do with this item.')
        else:
            dialog.ok(str(len(confirmed))+" confirmed as depreciated", 'There are '+str(len(confirmed))+' items on your system that are confirmed as broken and are not going to be updated. Please view the following list of add-ons affected and then press back and you can decide what to do with them.')
        cleantext = clean_text_box(confirmed)
        Text_Boxes('DEPRECIATED CONTENT','The following items are confirmed as broken, they are no longer working and they are in such a bad way they are not due to come back - this is often due to website closures.[CR][CR][COLOR=dodgerblue]WARNING:[/COLOR] Keeping old content on your system (especially repositories) '
            'is a serious security flaw and opens a way for hackers to easily manipulate your device. It would be very simple for a hacker to wipe your device or even worse steal any sensitive data on there so always make sure you remove any depreciated addons & repos.[CR][CR]'+cleantext+'[CR][CR][COLOR=dodgerblue]'
            'Are you the developer of something listed here?[/COLOR][CR]If you feel something is incorrectly tagged please post on the noobsandnerds forum with any proof you can provide and the team will look into updating the records. The list is compiled from a mixture of community driven reports combined with auto-generated scans on repos and as with any AV program there is a chance of false positives.')
        choice = dialog.yesno('All or Selective','Would you like to automatically quarantine all of these items or would you prefer to choose which ones to remove?',yeslabel='quarantine ALL', nolabel='Select Items')
        if choice:
            quarantine('all',confirmed)
        else:
            quarantine('select',confirmed)

    if len(unconfirmed)>0:
        if len(unconfirmed) == 1:
            dialog.ok(str(len(unconfirmed))+" unconfirmed broken", 'There is 1 item on your system that\'s marked as broken in the Add-on Portal but it has not yet been fully verified as being completely dead. Take a look at the following list and then decide what you want to do.')
        else:
            dialog.ok(str(len(unconfirmed))+" unconfirmed broken", 'There is '+str(len(unconfirmed))+' items on your system that are marked as broken in the Add-on Portal but have not yet been fully verified as being completely dead. Take a look at the following list and then decide what you want to do.')
        cleantext = clean_text_box(unconfirmed)
        Text_Boxes('CONTENT MARKED AS DELETED','The following items have been marked up as depreciated (no longer working or no longer available). The content in here is unconfirmed by the NaN staff but the automated script that searches repo\'s could no longer locate these particular addons. '
            'The most likely scenario is that a developer has deliberately pulled the add-on and it is no longer available.[CR][CR][COLOR=dodgerblue]WARNING:[/COLOR] Keeping old content on your system (especially repositories) '
            'is a serious security flaw and opens a way for hackers to easily manipulate your device. It would be very simple for a hacker to wipe your device or even worse steal any sensitive data on there so always make sure you remove any depreciated addons & repos.[CR][CR]'+cleantext+'[CR][CR][COLOR=dodgerblue]'
            'Are you the developer of something listed here?[/COLOR][CR]If you feel something is incorrectly tagged please post on the noobsandnerds forum with any proof you can provide and the team will look into updating the records. The list is compiled from a mixture of community driven reports combined with auto-generated scans on repos and as with any AV program there is a chance of false positives.')
        choice = dialog.yesno('All or Selective','Would you like to automatically quarantine all of these items or would you prefer to choose which ones to remove?',yeslabel='quarantine ALL', nolabel='Select Items')
        if choice:
            quarantine('all',unconfirmed)
        else:
            quarantine('select',unconfirmed)

    if len(unknown)>0:
        cleantext = clean_text_box(unknown)
        if len(unknown) == 1:
            itemtext = 'There is 1 item on your system'
        else:
            itemtext = 'There are '+str(len(unknown))+' items'
        dialog.ok(str(len(unknown))+" unknown add-ons", itemtext+' on your system that the Add-on Portal has no record of. Please consider updating the Portal with details of these at [COLOR=dodgerblue]noobsandnerds.com[/COLOR]. Thank you.')
        Text_Boxes('UNKNOWN ADD-ONS','The following items have not been found in the Add-on Portal. You may want to check the legitimacy of these add-ons, if you\'re happy they are from legitimate sources please help the community by adding the details to '
            'the Add-on Portal at [COLOR=dodgerblue]www.noobsandnerds.com[/COLOR]. If you are a registered member with a minimum of 5 posts you can update add-on details yourself (including adding YouTube videos, settings genres, countries etc.) but if you prefer you can just post details '
            'on the forum and a member of the team will be happy to add the content to the Portal for you.[CR][CR]'+cleantext)
        if len(unknown) == 1:
            choice = dialog.yesno('Unknown Add-on','Would you like to quarantine this item?')
            if choice:
        	    quarantine('all',unknown)
        else:
            choice = dialog.yesno('Unknown Add-ons','Would you like to quarantine some of these items? If you click yes you can go through and select which ones you want quarantined.')
            if choice:
        	    quarantine('select',unknown)

    if len(versionupdate)>0:
        if len(versionupdate) == 1:
            oneitem = versionupdate[0]
            dialog.ok("update available", '[COLOR=dodgerblue]'+oneitem[0]+'[/COLOR] is outdated and there is a newer version available. Please click OK so we can check if the relevant repo is installed.')
        else:
            dialog.ok(str(len(versionupdate))+" updates available", 'There are '+str(len(versionupdate))+' items on your system that are outdated and have newer versions available. Please select what you want to do for each one...')
        update_items(versionupdate,existing)
    dialog.ok('Scan Complete','Please consider helping out the community by updating the Add-on Portal (or noobsandnerds team) of of any new add-on details you have details for. Broken, deleted, malicious... any info you can give will help others. Thank you.')
##########################################################################################
# Parse the array and format into a readable text file to display on screen
def clean_text_box(textlist):
    block   =   ''
    for item in textlist:
        counter =   0
        size    =   len(item)
        while counter < size-1:
            if counter == 0:
                block += '[COLOR=gold]'+item[counter]+':[/COLOR]     '
            elif counter == 3:
                block += '[CR][COLOR=dodgerblue]Details:[/COLOR] '+item[counter]+'[CR]'
            else:
                block += item[counter]+'   '
            counter += 1
        block += '[CR]'
    return block
##########################################################################################
# quarantine add-ons in the list
def quarantine(mode,addonarray):
    global reloadprofile
    if not os.path.exists(quarantine_path):
        os.makedirs(quarantine_path)
    for item in addonarray:
        choice = 1
        if mode == 'select':
            choice = dialog.yesno(item[0],'Would you like to quarantine[COLOR=dodgerblue]',item[0]+'[/COLOR]', nolabel='no', yeslabel='yes')
        if choice:
            try:
                os.rename(item[4], item[4].replace('addons'+os.sep,'quarantine'+os.sep))
                reloadprofile = 1
            except:
                choice = dialog.yesno(item[0]+': FAILED', 'It was not possible to move [COLOR=dodgerblue]'+item[0]+'[/COLOR]. It may be running as a service possibly slowing down your device, would you like to try and remove it completely?')
                if choice:
                    try:
                        shutil.rmtree(item[4])
                        reloadprofile = 1
                    except:
                        dialog.ok('FAILED TO REMOVE', 'It was not possible to remove [COLOR=dodgerblue]'+item[0]+'[/COLOR]. You will have to manually remove this, you\'ll most likely need to quit Kodi to do this.')
##########################################################################################
# Extract a zip with progre
def download(url, dest):
    dp = xbmcgui.DialogProgress()
    dp.create("Status...","Downloading Content",' ', ' ')
    dp.update(0)
    start_time=time.time()
    urllib.urlretrieve(url, dest, lambda nb, bs, fs: _pbhook(nb, bs, fs, dp, start_time))
##########################################################################################
# Dialog showing percentage of download complete and ETA  
def _pbhook(numblocks, blocksize, filesize, dp, start_time):
    try: 
        percent = min(numblocks * blocksize * 100 / filesize, 100) 
        currently_downloaded = float(numblocks) * blocksize / (1024 * 1024) 
        kbps_speed = numblocks * blocksize / (time.time() - start_time) 
        if kbps_speed > 0: 
            eta = (filesize - numblocks * blocksize) / kbps_speed 
        else: 
            eta = 0 
        kbps_speed = kbps_speed / 1024 
        total = float(filesize) / (1024 * 1024) 
        mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total) 
        e = 'Speed: %.02f Kb/s ' % kbps_speed 
        e += 'ETA: %02d:%02d' % divmod(eta, 60) 
        dp.update(percent, mbs, e)
    except: 
        percent = 100 
        dp.update(percent) 
    if dp.iscanceled(): 
        dp.close()
##########################################################################################
# Loop through the list of add-ons that require updating and check the correct repo is installed
def update_items(versionupdate, existing):
    for item in versionupdate:
        if not item[4] in existing:
            choice = dialog.yesno(item[0],'The Add-on Portal is showing this as being available on the following repository: [COLOR=dodgerblue]'+item[4],'[/COLOR]Would you like to install this repo so you can update?')
            if choice:
#                try:
                    download('https://github.com/noobsandnerds/noobsandnerds/blob/master/zips/'+item[4]+'/'+item[4]+'-0.0.0.1.zip?raw=true',os.path.join(packages,item[4]+'.zip'))
                    zin = zipfile.ZipFile(os.path.join(packages,item[4]+'.zip'), 'r')
                    zin.extractall(ADDONS)
                    existing.append(item[4])
 #               except:
  #                  dialog.ok('FAILED TO INSTALL','Sorry there was a problem trying to install this repository, please try searching on the web for an update. If you find one please update the team at noobsandnerds.com so they can update the portal details. Thank you.')
    xbmc.executebuiltin( 'UpdateLocalAddons' )
    xbmc.executebuiltin( 'UpdateAddonRepos' )
    dialog.ok ('Updated Pushed', 'The command to check for updates has been sent, take a look in the following window to make sure no new updates are available, if they are you may want to update.')
    xbmc.executebuiltin('ActivateWindow(10040,"addons://",return)')
##########################################################################################
def addDir(type,name,url,mode,iconimage = '',fanart = '',video = '',description = ''):    
    if fanart == '':
        fanart = mainfanart

    if iconimage == '':
        iconimage = os.path.join(ADDONS,AddonID,'icon.png')
    elif not os.path.exists(os.path.join(artpath,iconimage)):
        iconimage = os.path.join(ADDONS,AddonID,'icon.png')
    else:
        iconimage = os.path.join(artpath,iconimage)

    u   = sys.argv[0]
    u += "?url="            +urllib.quote_plus(url)
    u += "&mode="           +str(mode)
    u += "&name="           +urllib.quote_plus(name)
    u += "&iconimage="      +urllib.quote_plus(iconimage)
    u += "&fanart="         +urllib.quote_plus(fanart)
    u += "&video="          +urllib.quote_plus(video)
    u += "&description="    +urllib.quote_plus(description)
        
    ok  = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
    liz.setProperty( "Fanart_Image", fanart )
    liz.setProperty( "Build.Video", video )
    xbmc.log('### icon path: '+iconimage)
    xbmc.log('### fanart path: '+fanart)
    
    if 'folder' in type:
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    
    else:
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    
    return ok
##########################################################################################    
# Initial start routine, add the menu structure
def restore():
    global reloadprofile
    qlist_fail = ''
    choice 	   = dialog.yesno('Quarantine Vault','Would you like to restore everything from your quarantinen vault or just individual items?', yeslabel='Everything', nolabel='Individual Items')
    if choice:
    	for item in q_list:
            path   = os.path.join(HOME,'quarantine',item)
            try:
                os.rename(path,path.replace('quarantine','addons'))
                reloadprofile = 1
            except:
            	qlist_fail += '[COLOR=gold]'+item+' -[/COLOR] Unable to restore[CR]'
    else:
        choice = dialog.select('Select item to restore',q_list)
        path   = os.path.join(HOME,'quarantine',q_list[choice])
        try:
            os.rename(path,path.replace('quarantine','addons'))
            reloadprofile = 1
        except:
            dialog.ok('FAILED', 'Sorry it was not possible to restore, check you haven\'t already reinstalled this item')
    if qlist_fail != '':
         Text_Boxes('UNABLE TO RESTORE','The items listed below could not be restored. The most likely cause for this is the user attempting to reinstall via other means. Please remove any instance of these items from your addons folder and run this function again.[CR][CR]')
##########################################################################################    
# Initial start routine, add the menu structure
def start():
    addDir('','Scan my system','','startscan','scan.png','','','')
    addDir('','Show add-ons running a service','','services','service.png','','','')
    if len(q_list) > 0:
        addDir('','Restore quarantined items','','restore','restore.png','','','')
##########################################################################################
# Start the scan of repo's
def startscan():
    onlinemaster    =   []
    localmaster     =   grab_installed()
    onlineraw       =   Open_URL('http://noobsandnerds.com/TI/AddonPortal/brokenlist.php',10).replace('], ]',']]')
    onlinemaster    =   eval(str(onlineraw))
    check_content(localmaster, onlinemaster)
##########################################################################################
# Get params and clean up into string or integer
def Get_Params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param
##########################################################################################
def services():
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    servicelist = ''
    for name in os.listdir(ADDONS):
        currentxml	=	(os.path.join(ADDONS,name,'addon.xml'))
        if os.path.exists(currentxml):
            readfile 	=	open(currentxml,'r')
            xmlcontent	=	readfile.read()
            readfile.close()
            namematch   = re.compile(' name="(.+?)"').findall(xmlcontent)
            addonname   = namematch[0] if (len(namematch) > 0) else 'Unknown (folder: '+name+')'
            if 'xbmc.service' in xmlcontent:
                startmatch	 = re.compile('start="(.+?)"').findall(xmlcontent)
                startpoint   = startmatch[0] if (len(startmatch) > 0) else 'Unknown'
                servicelist += '[COLOR=gold]'+addonname+' -[/COLOR] Startup Point: '+startpoint+'[CR]'
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    if servicelist != '':
         Text_Boxes('SERVICES FOUND','The following items are coded to run some sort of service in the background. Whilst there are many legitimate reasons for running services (such as automated maintenance tasks) they can also be used for more dubious means such as data gathering or running malicious code. Even if the author has perfectly good intentions a badly written service can be the cause of many problems within Kodi ranging from slowdowns to inability to play certain content. '
         	'As mentioned there are plenty of legitimate reasons to add a service to an add-on but take a look at the list below and if you see any that don\'t seem to warrant having a service running contact the developer of that add-on so they can explain why it\'s there. The chances are there is a perfectly good reason but it\'s always better to be safe than sorry.[CR][CR]'+servicelist)
##########################################################################################
description=None
iconimage=None
mode=None
url=None
video=None
params=Get_Params()

try:
    description=urllib.unquote_plus(params["description"])
except:
    pass
try:
    iconimage=urllib.unquote_plus(params["iconimage"])
except:
    pass
try:    
    mode=str(params["mode"])
except:
    pass
try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    video=urllib.unquote_plus(params["video"])
except:
    pass

if os.path.exists(quarantine_path):
    for name in os.listdir(quarantine_path):
        xbmc.log(name)
        if os.path.exists(os.path.join(quarantine_path,name,'addon.xml')):
            q_list.append(name)

if not os.path.exists(packages):
    os.makedirs(packages)

if mode     ==  None        : start()
elif mode   ==  'restore'   : restore()
elif mode   ==  'startscan' : startscan()
elif mode   ==  'services'  : services()

# If anything has been quarantined we need to reload the profile so the addons db updates.
if reloadprofile:
    if os.path.exists(temp):
        try:
            shutil.rmtree(temp)
        except:
            try:
                os.remove(cookies)
            except:
                dialog.ok('Failed to remove cached data','If you still see your quarantined add-ons when navigating through Kodi you may need to delete your cache folder manually.')
    xbmc.executebuiltin("LoadProfile(Master user,)")

xbmcplugin.endOfDirectory(int(sys.argv[1]))