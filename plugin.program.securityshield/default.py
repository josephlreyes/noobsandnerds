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

##########################################################################################
# Global imports
import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon
import os, sys, shutil, zipfile, time, unicodedata, fnmatch, base64
import pyxbmct.addonwindow as pyxbmct
##########################################################################################
AddonID         =  'plugin.program.securityshield'
AddonName       =  'Security Shield'
ADDON           =  xbmcaddon.Addon(id=AddonID)
dialog          =  xbmcgui.Dialog()
dp              =  xbmcgui.DialogProgress()
HOME            =  xbmc.translatePath('special://home')
PROFILE         =  xbmc.translatePath('special://profile')
USERDATA        =  xbmc.translatePath('special://userdata')
ADDON_DATA      =  os.path.join(PROFILE,'addon_data')
ADDONS          =  os.path.join(HOME,'addons')
quarantine_path =  os.path.join(HOME,'quarantine')
shieldfolder    =  os.path.join(ADDON_DATA,AddonID)
whitelistpath   =  os.path.join(shieldfolder,'whitelist.txt')
mainfanart      =  os.path.join(ADDONS,AddonID,'Fanart.jpg')
mainicon        =  os.path.join(ADDONS,AddonID,'icon.png')
artpath         =  os.path.join(ADDONS,AddonID,'resources')
checkicon       =  os.path.join(artpath,'check.png')
packages        =  os.path.join(ADDONS,'packages')
temp            =  xbmc.translatePath('special://temp')
cookies         =  os.path.join(temp,'cookies.dat')
log_path        =  xbmc.translatePath('special://logpath/')
updateicon      =  os.path.join(artpath,'update.png')
dialog_bg       =  os.path.join(artpath,'background.png')
black           =  os.path.join(artpath,'black.png')
kodiv           =  float(xbmc.getInfoLabel("System.BuildVersion")[:4])
reloadprofile   =  0
emptylist       =  0
ACTION_MOVE_UP   = 3
ACTION_MOVE_DOWN = 4
##########################################################################################
# Create arrays for our final results
versionupdate   =   []
blocked         =   []
confirmed       =   []
unconfirmed     =   []
unknown         =   []
existing        =   []
q_list          =   []
wl_array        =   []
wl_desc         =   []
wl_images       =   []
wl_add          =   []
##########################################################################################
# Populate the quarantine array
if os.path.exists(quarantine_path):
    for name in os.listdir(quarantine_path):
        if os.path.exists(os.path.join(quarantine_path,name,'addon.xml')):
            q_list.append(name)
##########################################################################################
# Create the directories required on first run
if not os.path.exists(packages):
    os.makedirs(packages)

if not os.path.exists(shieldfolder):
    os.makedirs(shieldfolder)
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
# Add a directory, can either be a folder type or standalone using the first param as "folder" for folder
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
    
    if 'folder' in type:
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    
    else:
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    
    return ok
##########################################################################################
# Advanced menu
def advanced():
    addDir('',string(30127), '', 'check_addon_data', 'check_addon_data.png','','','')
    addDir('',string(30112), '', 'system_process', 'system_process.png','','','')
    addDir('',string(30086), '', 'services', 'service.png','','','')
    addDir('',string(30126), '', 'decompile', 'decompile.png','','','')   
    if len(q_list) > 0:
        addDir('',string(30089), '', 'delete_quarantine', 'restore.png','','','')
##########################################################################################    
# Check addon_data folders against installed addons
def check_addon_data():
    data_array  = []
    name_array  = []
    image_array = []
    desc_array  = []
    final_array = []

    for item in os.listdir(ADDON_DATA):
        data_path = os.path.join(ADDON_DATA, item)
        if os.path.isdir(data_path):
            try:
                addon_check = xbmcaddon.Addon(id=item)
                addon_desc  = addon_check.getAddonInfo('description')
            except:
                data_array.append(data_path)
                name_array.append(item)
                image_array.append(mainicon)
                desc_array.append('No add-on found with the id: [COLOR=dodgerblue]%s[/COLOR]' % item)
    if len(data_array) == 0:
        dialog.ok(string(30127),string(30128))
    else:
        if dialog.yesno(string(30127),string(30129)%len(data_array)):
            clean_folders(data_array)
        else:
            to_remove = multiselect(string(30130),name_array,image_array,desc_array)
            for item in to_remove:
                final_array.append(data_array[item])
            clean_folders(final_array)
##########################################################################################    
# Loop through each item in our local array and check against online array
def check_content(localmaster, onlinemaster):
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
            unknown.append([name, addonid, version,string(30000),path])
    xbmc.executebuiltin("Dialog.Close(busydialog)")

    if len(blocked)>0:
        if len(blocked) == 1:
            dialog.ok(string(30001), string(30002))
        else:
            dialog.ok(str(len(blocked))+string(30003), string(30004) % str(len(blocked)))
        cleantext = clean_text_box(blocked)
        Text_Boxes(string(30005), string(30006) % cleantext)
        choice = dialog.yesno(string(30007),string(30008),yeslabel=string(30009), nolabel=string(30010))
        if choice:
            quarantine('all',blocked)
        else:
            quarantine('select',blocked)

    if len(confirmed)>0:
        if len(confirmed) == 1:
            dialog.ok(str(len(confirmed))+string(30011), string(30012))
        else:
            dialog.ok(str(len(confirmed))+string(30011), string(30013) % str(len(confirmed)))
        xbmc.log(str(confirmed))
        cleantext = clean_text_box(confirmed)
        Text_Boxes(string(30014), string(30015) % cleantext)
        choice = dialog.yesno(string(30007),string(30008),yeslabel=string(30009), nolabel=string(30010))
        if choice:
            quarantine('all',confirmed)
        else:
            quarantine('select',confirmed)

    if len(unconfirmed)>0:
        if len(unconfirmed) == 1:
            dialog.ok(str(len(unconfirmed))+string(30017), string(30018))
        else:
            dialog.ok(str(len(unconfirmed))+string(30017), string(30019) % str(len(unconfirmed)))
        cleantext = clean_text_box(unconfirmed)
        Text_Boxes(string(30020), string(30021) % cleantext)
        choice = dialog.yesno(string(30007),string(30008),yeslabel=string(30009), nolabel=string(30010))
        if choice:
            quarantine('all',unconfirmed)
        else:
            quarantine('select',unconfirmed)

    if len(unknown)>0:
        cleantext = clean_text_box(unknown)
        if len(unknown) == 1:
            itemtext = string(30016)
        else:
            itemtext = string(30022) % str(len(unknown))
        dialog.ok(string(30023) % str(len(unknown)), string(30024) % itemtext)
        Text_Boxes(string(30025), string(30026) % cleantext)
        if len(unknown) == 1:
            choice = dialog.yesno(string(30027), string(30028))
            if choice:
                quarantine('all',unknown)
        else:
            choice = dialog.yesno(string(30029), string(30030))
            if choice:
                quarantine('select',unknown)

    if len(versionupdate)>0:
        if len(versionupdate) == 1:
            oneitem = versionupdate[0]
            dialog.ok(string(30031), string (30032) % oneitem[0])
        else:
            dialog.ok(string(30033) % str(len(versionupdate)), string(30034) % str(len(versionupdate)))
        update_items(versionupdate,existing)
    if len(unknown) > 0 or len(unconfirmed) > 0 or len(confirmed) > 0 or len(blocked) > 0:
        dialog.ok(string(30035), string(30036))
    elif sys.argv[1] != 'silent':
        dialog.ok(string(30037), string(30038))
##########################################################################################
# Loop through an array of paths and delete them
def clean_folders(folder_array):
    counter = 0
    for item in folder_array:
        xbmc.log('### Attempting to remove: %s' % item)
        try:
            shutil.rmtree(item)
            counter += 1
        except Exception as e:
            xbmc.log('Failed to remove %s: %s' % (item, e))
    dialog.ok(string(30127),string(30131) % (counter, len(folder_array)))
##########################################################################################
# Parse the array and format into a readable text file to display on screen
def clean_text_box(textlist):
    block   =   ''
    for item in textlist:
        name = unicodedata.normalize('NFKD',unicode(item[0],"ISO-8859-1")).encode("ascii","ignore")
#        name = item[0].text.encode('ascii', 'ignore')
        block += '[COLOR=gold]%s[/COLOR] (%s)[CR]' % (name, item[1])
    return block
##########################################################################################
# Permanently delete items from the quarantine vault
def decompile():
    success = 1
    choice  = dialog.yesno(string(30115), string(30116),yeslabel=string(30117), nolabel=string(30118))
    if choice:
        filename = xbmcgui.Dialog().browse(1, string(30119), 'files', '.py', False, False, ADDONS)
        content  = readcontents(filename)
        if content.startswith('import base64;exec base64.b64decode('):
            content = unobfuscate(filename,content)
            if not content.startswith('import base64;exec base64.b64decode('):
                saveas    = dialog.browse(3, string(30120), 'files', '', False, False,HOME)
                savefile  = os.path.join(saveas,'unobfuscated.py')
                writefile = open(savefile, 'w')
                writefile.write(content)
                writefile.close()
                dialog.ok(string(30121),string(30122) % savefile)
            else:
                dialog.ok(string(30123),string(30124))
        else:
            dialog.ok(string(30123),string(30124))
##########################################################################################
# Permanently delete items from the quarantine vault
def delete_quarantine():
    if os.path.exists(quarantine_path) and len(q_list)>0:
        choice  = dialog.yesno(string(30040), string(30041),yeslabel=string(30042), nolabel=string(30043))
        if choice:
            choice = dialog.yesno(string(30044), string(30045))
            if choice:
                try:
                    shutil.rmtree(quarantine_path)
                    dialog.ok(string(30046),string(30047))
                except:
                    dialog.ok(string(30048), string(30049))

        else:
            choice  = dialog.select(string(30050),q_list)
            choice2 = dialog.yesno(string(30044), string(30051) % q_list[choice])
            if choice2:
                try:
                    shutil.rmtree(os.path.join(quarantine_path,q_list[choice]))
                    dialog.ok(string(30046), string(30052))
                except:
                    dialog.ok(string(30048), string(30049))
    else:
        dialog.ok(string(30053), string(30054))
##########################################################################################
# Download items with progress bar
def download(url, dest):
    dp = xbmcgui.DialogProgress()
    dp.create(string(30055), string(30056), ' ', ' ')
    dp.update(0)
    start_time=time.time()
    urllib.urlretrieve(url, dest, lambda nb, bs, fs: _pbhook(nb, bs, fs, dp, start_time))
##########################################################################################
# Loop through subfolders and find files
def findfiles (path, filter):
    for root, dirs, files in os.walk(path):
        for file in fnmatch.filter(files, filter):
            yield os.path.join(root, file)
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
# Grab a list of all the content instsalled in our Kodi addons folder
def grab_installed():
    locallist = []
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    for name in os.listdir(ADDONS):
# copy all the repo's to repopath folder in userdata and zip up with version number
        if not 'packages' in name and not 'cygpfi' in name and name not in wl_array:
            currentpath =   os.path.join(ADDONS,name)
            currentfile =   os.path.join(currentpath,'addon.xml')
            
            if os.path.exists(currentfile):
                content = readcontents(currentfile)

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
                srcomments = string(30057)
                if 'superrepo' in addonid:
                    blocked.append([name,addonid,localversionmatch,srcomments,currentpath])
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    return locallist
##########################################################################################
# Reload the current running profile
def load_profile():
    current    = xbmc.getInfoLabel('System.ProfileName')
    xbmc.executebuiltin('LoadProfile(%s)' % current)
##########################################################################################
# Find out what version of Kodi is running and return the correct log path
def log_check():
    if os.path.exists(os.path.join(log_path,'xbmc.log')):
        log_path_new = os.path.join(log_path,'xbmc.log')
    elif os.path.exists(os.path.join(log_path,'kodi.log')):
        log_path_new = os.path.join(log_path,'kodi.log')
    elif os.path.exists(os.path.join(log_path,'spmc.log')):
        log_path_new = os.path.join(log_path,'spmc.log')
    elif os.path.exists(os.path.join(log_path,'tvmc.log')):
        log_path_new = os.path.join(log_path,'tvmc.log')
    try:
        localfile = open(log_path_new, mode='r')
        content   = localfile.read()
        localfile.close()
        return content
    except:
        return False
##########################################################################################
# Multiselect Dialog - works with gotham onwards
def multiselect(title, list, images, description):
    global pos
    global listicon
    class MultiChoiceDialog(pyxbmct.AddonDialogWindow):
        def __init__(self, title="", items=None, images=None, description=None):
            super(MultiChoiceDialog, self).__init__(title)
            self.setGeometry(1100, 700, 20, 20)
            self.selected = []
            self.set_controls()
            self.connect_controls()
            self.listing.addItems(items or [])
            self.set_navigation()
            self.connect(ACTION_MOVE_UP, self.update_list)
            self.connect(ACTION_MOVE_DOWN, self.update_list)
            
        def set_controls(self):
            Background  = pyxbmct.Image(dialog_bg, aspectRatio=0) # set aspect ratio to stretch
            Background.setImage(dialog_bg)
            self.listing = pyxbmct.List(_imageWidth=15)
            self.placeControl(Background, 0, 0, rowspan=20, columnspan=20)
            Icon=pyxbmct.Image(images[0], aspectRatio=2) # set aspect ratio to keep original
            Icon.setImage(images[0])
            self.placeControl(Icon, 0, 11, rowspan=8, columnspan=8, pad_x=10, pad_y=10)
            self.textbox = pyxbmct.TextBox()
            self.placeControl(self.textbox, 8, 11, rowspan=9, columnspan=9, pad_x=10, pad_y=10)
            self.textbox.setText(description[0])
            self.textbox.autoScroll(5000, 2000, 8000)
            self.ok_button = pyxbmct.Button("OK")
            self.placeControl(self.ok_button, 17, 13, pad_x=10, pad_y=10, rowspan=2, columnspan=3)
            self.cancel_button = pyxbmct.Button("Cancel")
            self.placeControl(self.cancel_button, 17, 16, pad_x=10, pad_y=10, rowspan=2, columnspan=3)
            self.placeControl(self.listing, 0, 0, rowspan=20, columnspan=10, pad_y=10) # grid reference, start top left and span 9 boxes down and 5 across

        def connect_controls(self):
            self.connect(self.listing, self.check_uncheck)
            self.connect(self.ok_button, self.ok)
            self.connect(self.cancel_button, self.close)

        def set_navigation(self):
            self.listing.controlLeft(self.ok_button)
            self.listing.controlRight(self.ok_button)
            self.ok_button.setNavigation(self.listing, self.listing, self.cancel_button, self.cancel_button)
            self.cancel_button.setNavigation(self.listing, self.listing, self.ok_button, self.ok_button)
            if self.listing.size():
                self.setFocus(self.listing)
            else:
                self.setFocus(self.cancel_button)
            
        def update_list(self):
            blackout = pyxbmct.Image(black, aspectRatio=0) # set aspect ratio to stretch
            blackout.setImage(black)
            self.placeControl(blackout, 0, 11, rowspan=8, columnspan=8, pad_x=10, pad_y=10)
            pos      = self.listing.getSelectedPosition()
            listicon = images[pos]
            Icon     = pyxbmct.Image(listicon, aspectRatio=2)
            Icon.setImage(listicon)
            self.placeControl(Icon, 0, 11, rowspan=8, columnspan=8, pad_x=10, pad_y=10)
            self.textbox.setText(urllib.unquote(description[pos]))

        def check_uncheck(self):
            list_item = self.listing.getSelectedItem()
            if list_item.getLabel2() == "checked":
                list_item.setIconImage("")
                list_item.setLabel2("unchecked")
            else:
                list_item.setIconImage(checkicon)
                list_item.setLabel2("checked")

        def ok(self):
            self.selected = [index for index in xrange(self.listing.size())
                            if self.listing.getListItem(index).getLabel2() == "checked"]
            super(MultiChoiceDialog, self).close()

        def close(self):
            self.selected = []
            super(MultiChoiceDialog, self).close()
            
    dialog = MultiChoiceDialog(title, list, images, description)
    dialog.doModal()
    return dialog.selected
    del dialog
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
        dialog.ok(string(30058), string(30059))
        return
##########################################################################################
# quarantine add-ons in the list
def quarantine(mode,addonarray):
    patharray     = []
    imagearray    = []
    descarray     = []
    namearray     = []
    to_quarantine = []
    finalarray    = []
    if not os.path.exists(quarantine_path):
        os.makedirs(quarantine_path)

    if mode == 'select' and len(addonarray)>0:
        for item in addonarray:
            length = len(item)
            patharray.append(item[length-1])
            namearray.append(item[0])
            descarray.append(item[3])
            imagearray.append(os.path.join(item[length-1],'icon.png'))
        to_quarantine = multiselect(string(30060),namearray,imagearray,descarray)
        for item in to_quarantine:
            finalarray.append([namearray[item], patharray[item]])

    elif len(addonarray)>0:
        for item in addonarray:
            length = len(item)
            finalarray.append([item[0], item[length-1]])
    xbmc.log(str(finalarray))

    move_to_vault(finalarray)
##########################################################################################
# move add-ons to the vault
def move_to_vault(array):
    global reloadprofile
    for item in array:
        try:
            os.rename(item[1], item[1].replace('addons%s' % os.sep, 'quarantine%s' % os.sep))
            reloadprofile = 1
        except:
            choice = dialog.yesno(string(30061) % item[0], string(30062) % item[0])
            if choice:
                try:
                    shutil.rmtree(item[1])
                    reloadprofile = 1
                except:
                    dialog.ok(string(30063), string(30064) % item[0])
##########################################################################################
# quarantine any repos failing to resolve
def quarantine_unresolved(addonarray):
    global reloadprofile
    for item in addonarray:
        choice = dialog.yesno(item, string(30060),'[COLOR=dodgerblue]%s[/COLOR]' % item)
        addonpath = os.path.join(ADDONS,item)
        if choice:
            try:
                os.rename(addonpath, addonpath.replace('addons%s' % os.sep, 'quarantine%s' % os.sep))
                reloadprofile = 1
            except:
                choice = dialog.yesno(string(30048), string(30062) % item)
                if choice:
                    try:
                        shutil.rmtree(item)
                        reloadprofile = 1
                    except:
                        dialog.ok(string(30063), string(30064) % item)
##########################################################################################
# Check log for installed repo that fail to pull updates
def repo_check():
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    xbmc.executebuiltin('UpdateAddonRepos')
    finallist   = []
    repocount   = 0
    logcontents = log_check()
    if logcontents:
# Count how many repos are installed, it takes 1 second per repo to print details to log
        for name in os.listdir(ADDONS):
            if 'repo' in name:
                repocount +=1
# Add a sleep so the log has had enough time to fill with data
        notify(string(30065), string(30066) % str(repocount), 10000, updateicon)
        if repocount > 100:
            time.sleep((repocount/2)+10)
        elif repocount ==0:
            pass
        elif repocount <101:
            time.sleep(repocount+10)
# Check log again after we've waited for repos to update
        logcontents = log_check()
        errorlinematch  = re.compile('CRepositoryUpdateJob(.+?)failed', re.DOTALL).findall(logcontents)
        for item in errorlinematch:
            brokenrepo = item.replace('[','').replace(']','').replace(' ','').replace('/','').replace('\\','')
            if not brokenrepo in finallist:
                finallist.append(brokenrepo)
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        if len(finallist) > 0:
            repolist = ''
            for name in finallist:
                repolist += '%s[CR]' % name

            Text_Boxes(string(30067), string(30068) % repolist)
            choice = dialog.yesno(string(30069), string(30070))
            if choice:
                quarantine_unresolved(finallist)
        else:
            dialog.ok(string(30071), string(30072))
    else:
        dialog.ok(string(30073), string(30074))
##########################################################################################
# Initial start routine, add the menu structure
def restore():
    global reloadprofile
    qlist_fail = ''
    choice     = dialog.yesno(string(30040), string(30110), yeslabel=string(30075), nolabel=string(30076))
    if choice:
        for item in q_list:
            try:
                path   = os.path.join(HOME,'quarantine',item)
                os.rename(path,path.replace('quarantine','addons'))
                reloadprofile = 1
            except:
                qlist_fail += string(30077) % item
    else:
        patharray  = []
        imagearray = []
        descarray  = []
        for item in q_list:
            itempath   = os.path.join(HOME,'quarantine',item)
            image      = os.path.join(itempath,'icon.png')
            patharray.append(itempath)
            imagearray.append(image)
            descarray.append(string(30111))
        choice = multiselect(string(30078),q_list, imagearray, descarray)
        for item in choice:
            path   = patharray[item]
            try:
                os.rename(path,path.replace('quarantine','addons'))
                reloadprofile = 1
            except:
                dialog.ok(string(30048), string(30079))
    if qlist_fail != '':
        Text_Boxes(string(30080), string(30081))
##########################################################################################    
# Check which add-ons are running as services
def services():
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    servicelist = ''
    for name in os.listdir(ADDONS):
        currentxml  =   (os.path.join(ADDONS,name,'addon.xml'))
        if os.path.exists(currentxml):
            xmlcontent  = readcontents(currentxml)
            namematch   = re.compile(' name="(.+?)"').findall(xmlcontent)
            addonname   = namematch[0] if (len(namematch) > 0) else 'Unknown (folder: '+name+')'
            if 'xbmc.service' in xmlcontent:
                startmatch   = re.compile('start="(.+?)"').findall(xmlcontent)
                startpoint   = startmatch[0] if (len(startmatch) > 0) else 'Unknown'
                servicelist += '[COLOR=gold]%s -[/COLOR] Startup Point: %s[CR]' % (addonname, startpoint)
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    if servicelist != '':
         Text_Boxes(string(30082), string(30083) % servicelist)
##########################################################################################
# Initial start routine, add the menu structure
def start():
    addDir('',string(30084), '', 'startscan', 'scan.png','','','')
    addDir('',string(30085), '', 'repo_check', 'repo_check.png','','','')
    addDir('',string(30087), '', 'whitelist', 'whitelist.png','','','')
    if len(q_list) > 0:
        addDir('',string(30088), '', 'restore', 'restore.png','','','')
    addDir('folder',string(30125),'','advanced','advanced.png','','','')
##########################################################################################
# Start the scan of repo's
def startscan():
    onlinemaster    =   []
    localmaster     =   grab_installed()
    onlineraw       =   Open_URL('http://noobsandnerds.com/TI/AddonPortal/addonlist.php',30)
    addonarray      =   re.compile('#(.+?)~').findall(onlineraw)
    for item in addonarray:
        try:
            addon, status, version, repo, message = item.split(',')
            if str(message) == '1':
                message = 'No problems reported'
            elif str(message) == '2':
                message = 'Sorry no further details have been submitted, we just know it has been marked as potentially dangerous'
            elif str(message) == '3':
                message = 'Sorry no further details have been submitted, we just know it has been marked as deleted'
            onlinemaster.append([addon,status,version,repo,message])
        except Exception as e:
            xbmc.log(str(e))

    # onlinemaster    =   eval(str(onlineraw))
    check_content(localmaster, onlinemaster)
##########################################################################################
def string(string):
    return ADDON.getLocalizedString(string)
##########################################################################################    
# Check for add-ons that run a system process
def system_process():
    counter = 0
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    systemlist = '[COLOR=gold]Files Containing os.system():[/COLOR][CR]'
    processlist = '[CR][CR][COLOR=gold]Files Containing subprocess.call():[/COLOR][CR]'
    for pyfile in findfiles(ADDONS, '*.py'):
        if not pyfile.startswith(packages):
            content = readcontents(pyfile)
            content = unobfuscate(pyfile, content)
            if ('os.system(' in content or 'os . system(' in content) and not AddonID in pyfile:
                systemlist += pyfile.replace(ADDONS+os.sep,'')+'[CR]'
                counter += 1
            if  ('subprocess.call' in content or 'subprocess . call' in content or 'subprocess.Popen' in content or 'subprocess . Popen' in content) and not AddonID in pyfile:
                processlist += pyfile.replace(ADDONS+os.sep,'')+'[CR]'
                counter +=1
    if os.path.exists(os.path.join(PROFILE,'autoexec.py')):
        content = readcontents(os.path.join(PROFILE,'autoexec.py'))
        content = unobfuscate(pyfile, content)
        if 'os.system(' in content or 'os . system(' in content:
            systemlist += os.path.join(PROFILE,'autoexec.py').replace(HOME+os.sep,'')+'[CR]'
            counter += 1
        if  ('subprocess.call' in content or 'subprocess . call' in content or 'subprocess.Popen' in content or 'subprocess . Popen' in content):
            processlist += os.path.join(PROFILE,'autoexec.py').replace(HOME+os.sep,'')+'[CR]'
            counter +=1


    if systemlist == '[COLOR=gold]Files Containing os.system():[/COLOR][CR]':
        systemlist = ''

    if processlist == '[CR][CR][COLOR=gold]Files Containing subprocess.call():[/COLOR][CR]':
        processlist = ''

    if systemlist != '' or processlist != '':
        Text_Boxes(string(30114),string(30113) %counter+systemlist+processlist)
    xbmc.executebuiltin("Dialog.Close(busydialog)")
##########################################################################################
# Read content of a file and return as string
def readcontents(file):
    readfile = open(file,'r')
    content  = readfile.read()
    readfile.close()
    return content
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
# Create a Notification  
def notify(title, message, time=2000, icon=mainicon):
    xbmc.executebuiltin("XBMC.Notification(%s, %s, %s, %s)" % (title, message, time, icon))
##########################################################################################    
# Check for add-ons that run a system process
def unobfuscate(pyfile, content):
    count = 1
    while content.startswith('import base64;exec base64.b64decode('):
        xbmc.log('### Obfuscated addon: %s' % pyfile)
        xbmc.log('### Attempting to decompile, pass #%s' % count)
        content = content.replace("import base64;exec base64.b64decode('",'')
        content = content[:-2]
        if not AddonID in pyfile:
            try:
                newcontent = base64.b64decode(content)
                if newcontent.startswith('import base64;exec base64.b64decode('):
                    xbmc.log('### Still obfuscated after attempt %s, running through it again...' % count)
                else:
                    xbmc.log('### Successfully unobfuscated %s' % pyfile)
                    content = newcontent
            except:
                xbmc.log('### Failed to unobfuscate %s' % pyfile)
                break
            count += 1
    return content
##########################################################################################
# Loop through the list of add-ons that require updating and check the correct repo is installed
def update_items(versionupdate, existing):
    for item in versionupdate:
        if not item[4] in existing:
            choice = dialog.yesno(item[0], string(30090) % item[4], string(30091))
            if choice:
                try:
                    download('https://github.com/noobsandnerds/noobsandnerds/blob/master/zips/%s/%s-0.0.0.1.zip?raw=true' % (item[4], item[4]),os.path.join(packages,'%s.zip' % item[4]))
                    zin = zipfile.ZipFile(os.path.join(packages,'%s.zip' % item[4]), 'r')
                    zin.extractall(ADDONS)
                    existing.append(item[4])
                except:
                    dialog.ok(string(30092), string(30093))
    xbmc.executebuiltin( 'UpdateLocalAddons' )
    xbmc.executebuiltin( 'UpdateAddonRepos' )
    dialog.ok (string(30094), string(30095))
    xbmc.executebuiltin('ActivateWindow(10040,"addons://",return)')
##########################################################################################
# Add/Remove items in the whitelist
def whitelist():
    choice = dialog.yesno(string(30097), string(30098), yeslabel=string(30099), nolabel=string(30100))
    if choice:
        if not os.path.exists(whitelistpath) or emptylist == 1:
            dialog.ok(string(30101), string(30102), string(30103))
        else:
            choice = multiselect(string(30104),wl_array,wl_images,wl_desc); xbmc.log(str(choice)+' / '+str(len(choice)))
            if len(choice) > 0:
                with open(whitelistpath, "r+") as writefile:
                    content = writefile.read()
                    for wl in choice:
                        content = content.replace('%s|' % wl_array[wl],'')
                        print content
                    writefile.seek(0)
                    writefile.write(content)
                    writefile.truncate()
                    notify(string(30105), string(30106) % len(choice))
            else: notify(string(30105), string(30107))
    else:
        counter       = 0
        wl_add_desc   = []
        wl_add_images = []

        for name in os.listdir(ADDONS):
            if not name in wl_array and name != 'packages' and os.path.isdir(os.path.join(ADDONS,name)):
                wl_add.append(name)

# Grab add-on description and add to array
                try:
                    masteraddon     = xbmcaddon.Addon(id=wl_add[counter])
                    masterdesc      = masteraddon.getAddonInfo('description')
                except:
                    masterdesc      = 'No information available'
                wl_add_desc.append(masterdesc)

# Grab add-on icon and add to array
                mastericon      = os.path.join(ADDONS,name,'icon.png')
                wl_add_images.append(mastericon)
                counter += 1
        choice = multiselect(string(30109),wl_add, wl_add_images, wl_add_desc); xbmc.log(str(choice)+' / '+str(len(choice)))
        if len(choice) > 0:
            writefile = open(whitelistpath,'a')
            for wl in choice:
                writefile.write(wl_add[wl]+'|')
            writefile.close()
            notify(string(30105), string(30108) % len(choice))
        else: notify(string(30105), string(30107))
##########################################################################################
# Main add-on starts here
##########################################################################################
# Grab contents of whitelist and create description and image arrays for multi-select
if os.path.exists(whitelistpath):
    content = readcontents(whitelistpath)
    if content == '':
        emptylist = 1
    else:
        wl_array = content.split('|')
        wl_array = wl_array[:-1]

for item in wl_array:
# Grab add-on description and add to array
    try:
        masteraddon     = xbmcaddon.Addon(id=item)
        masterdesc      = masteraddon.getAddonInfo('description')
    except:
        masterdesc      = 'No information available'
    wl_desc.append(masterdesc)

# Grab add-on icon and add to array
    try:
        masteraddon     = xbmcaddon.Addon(id=item)
        mastericon      = masteraddon.getAddonInfo('icon')
    except:
        mastericon      = mainicon
    wl_images.append(mastericon)


if sys.argv[1]=='silent':
    while xbmc.Player().isPlaying():
        xbmc.sleep(5000)
    mode = 'startscan'
else:
    mode=None

description=None
iconimage=None
url=None
video=None
if sys.argv[1] != 'silent':
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

if mode     ==  None                : start()

elif mode   ==  'advanced'          : advanced()
elif mode   ==  'check_addon_data'  : check_addon_data()
elif mode   ==  'decompile'         : decompile()
elif mode   ==  'delete_quarantine' : delete_quarantine()
elif mode   ==  'repo_check'        : repo_check()
elif mode   ==  'restore'           : restore()
elif mode   ==  'services'          : services()
elif mode   ==  'startscan'         : startscan()
elif mode   ==  'system_process'    : system_process()
elif mode   ==  'whitelist'         : whitelist()
        
# If anything has been quarantined we need to reload the profile so the addons db updates.
if reloadprofile:
    if os.path.exists(temp):
        try:
            shutil.rmtree(temp)
        except:
            try:
                os.remove(cookies)
            except:
                pass
    load_profile()

if sys.argv[1]!='silent':
    xbmcplugin.endOfDirectory(int(sys.argv[1]))