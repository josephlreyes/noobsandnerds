# Rename Creator - will create a rename file for mc2xml & zap2xml with correct
# country code tagging. This is not required for TVPortal as the main add-on settings
# deal with renaming during import but it's intended for use with other EPG guides that
# want to use the universal naming conventions used in TVP so the same logos can be used.

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
import xbmc, xbmcgui, os, xbmcaddon, sys, urllib2, urllib
import re, shutil
import xml.etree.ElementTree as ET

import sys, traceback

# Global variables
AddonID      =  'script.tvportal.tools'
ADDON        =  xbmcaddon.Addon(id=AddonID)
ADDON2       =  xbmcaddon.Addon(id='script.tvportal')
HOME         =  xbmc.translatePath('special://home')
ADDONS       =  xbmc.translatePath('special://home/addons/')
USERDATA     =  xbmc.translatePath('special://profile/')
ADDON_DATA   =  xbmc.translatePath(os.path.join(USERDATA,'addon_data'))
dialog       =  xbmcgui.Dialog()
dp           =  xbmcgui.DialogProgress()
updateicon   =  os.path.join(ADDONS,'script.tvportal','resources','update.png')
log_path     =  xbmc.translatePath('special://logpath/')
renamefolder =  os.path.join(ADDON_DATA,AddonID,'XMLTV rename files')
errorlist    =  ['none']
countryarray =  [['','None'],['AF','Afghanistan'],['AL','Albania'],['DZ','Algeria'],['AO','Angola'],['AR','Argentina'],['AM','Armenia'],['AU','Australia'],
                ['AT','Austria'],['AZ','Azerbaijan'],['BS','Bahamas'],['BY','Belarus'],['BE','Belgium'],['BO','Bolivia'],['BA','Bosnia'],['BR','Brazil'],
                ['BG','Bulgaria'],['KM','Cambodia'],['CM','Cameroon'],['CA','Canada'],['CL','Chile'],['CN','China'],['CO','Colombia'],['CR','Costa Rica'],
                ['HR','Croatia'],['CU','Cuba'],['CY','Cyprus'],['CZ','Czech Republic'],['DK','Denmark'],['DO','Dominican Republic'],['EC','Ecuador'],['EG','Egypt'],
                ['SV','El Salvador'],['EE','Estonia'],['ET','Ethiopia'],['FI','Finland'],['FR','France'],['GA','Gabon'],['GM','Gambia'],['GE','Georgia'],
                ['DE','Germany'],['GH','Ghana'],['GR','Greece'],['GT','Guatemala'],['GN','Guinea'],['HT','Haiti'],['HN','Honduras'],['HK','Hong Kong'],
                ['HU','Hungary'],['IS','Iceland'],['IN','India'],['ID','Indonesia'],['IR','Iran'],['IQ','Iraq'],['IE','Ireland'],['IL','Israel'],['IT','Italy'],
                ['CI','Ivory Coast'],['JM','Jamaica'],['JP','Japan'],['JO','Jordan'],['KZ','Kazakhstan'],['KE','Kenya'],['XK','Kosovo'],['KW','Kuwait'],
                ['KG','Kyrgyzstan'],['LA','Laos'],['LV','Latvia'],['LB','Lebanon'],['LR','Liberia'],['LY','Libya'],['LI','Liechstenstein'],['LT','Lithuania'],
                ['LU','Luxembourg'],['MK','Macedonia'],['MG','Madagascar'],['MW','Malawi'],['MY','Malaysia'],['ML','Mali'],['MT','Malta'],['MU','Mauritius'],
                ['MX','Mexico'],['MD','Moldova'],['MN','Mongolia'],['ME','Montenegro'],['MA','Morocco'],['MZ','Mozambique'],['MM','Myanmar'],['NA','Namibia'],
                ['NP','Nepal'],['NL','Netherlands'],['NZ','New Zealand'],['NI','Nicaragua'],['NE','Niger'],['NG','Nigeria'],['NO','Norway'],['OM','Oman'],
                ['PK','Pakistan'],['PS','Palestine'],['PA','Panama'],['PY','Paraguay'],['PE','Peru'],['PH','Philippines'],['PL','Poland'],['PT','Portugal'],
                ['PR','Puerto Rico'],['QA','Qatar'],['RO','Romania'],['RU','Russia'],['RW','Rwanda'],['SA','Saudi Arabia'],['SN','Senegal'],['RS','Serbia'],
                ['SL','Sierra Leone'],['SG','Singapore'],['SK','Slovakia'],['SI','Slovenia'],['SO','Somalia'],['ZA','South Africa'],['KR','South Korea'],
                ['SS','South Sudan'],['ES','Spain'],['LK','Sri Lanka'],['SD','Sudan'],['SR','Suriname'],['SE','Sweden'],['CH','Switzerland'],['SY','Syria'],
                ['TW','Taiwan'],['TJ','Tajikistan'],['TZ','Tanzania'],['TH','Thailand'],['TG','Togo'],['TT','Trinidad and Tobago'],['TN','Tunisia'],['TR','Turkey'],
                ['TM','Turkmenistan'],['UG','Uganda'],['UA','Ukraine'],['AE','United Arab Emireates'],['GB','United Kingdom'],['US','United States'],['UY','Uruguay'],
                ['UZ','Uzbekistan'],['VE','Venezuela'],['VN','Vietnam'],['YE','Yemen'],['ZM','Zambia'],['ZW','Zimbabwe']]
##########################################################################################
# Return the last error
def Last_Error():
    errorstring = traceback.format_exc()
    xbmc.log("ERROR: "+errorstring)
    errorlinematch  = re.compile(': line (.+?),').findall(errorstring)
    errormatch      = errorlinematch[0] if (len(errorlinematch) > 0) else ''
    return errormatch
##########################################################################################
# Attempt to fix badly formed XML files with special characters in
def Fix_XML(errorline):
    xbmc.log("FIX_XML Function started")
    counter = 1
    rawfile = open(xmlpath,"r")
    lines = rawfile.readlines()
    rawfile.close()

    newfile = open(xmlpath,'w')
    for line in lines:
        counterstr = str(counter)
        if counterstr == errorline:
            xbmc.log("Removing Line "+counterstr)
        else:
            newfile.write(line)
        counter += 1
##########################################################################################
# Attempt to grab the contents of the XML and fix if badly formed
def Grab_XML_Tree(xpath):
    stop = 0
    while stop == 0:
        try:
            tree = ET.parse(xpath)
            stop = 1
        except:
            xbmc.log("Badly formed XML file, trying to fix...")
#            traceback.print_exc()
            traceerror = Last_Error()
            xbmc.log("Error List: "+str(errorlist))
            xbmc.log("Current Error: "+str(traceerror))
            xbmc.log("Error -1: "+errorlist[-1])
            if traceerror == errorlist[-1]:
                xbmc.log("Error matched one in array, lets stop the while loop")
                tree = ET.parse(xmlpath)
                stop = 1
            else:
                xbmc.log("New error, adding to array: "+traceerror)
                errorlist.append(traceerror)
                dialog.ok('Badly Formed XML File','You have an error on line [COLOR=dodgerblue]'+str(traceerror)+'[/COLOR] of your XML file. Press OK to continue scanning, we will then try and fix any errors.')
                Fix_XML(traceerror)
    return tree
##########################################################################################
# Create CSV for import and update chan.xml and cats.xml
def create_rename(channels,channelcount,xsource, country):
# Set a temporary list matching channel id with real name
    counter = 0
    if not os.path.exists(renamefolder):
        os.makedirs(renamefolder)
    xbmc.log("Creating List of channels")
    tempchans    = []
    xbmc.log("Channels Found: "+str(channelcount))
    writefile = open(os.path.join(renamefolder,xsource+'_'+country+'.ren'),'w')
    if xsource == 'Rovi':
        num = 3

    if country !='':
        country = ' ('+country+')'

    for channel in channels:
        donotadd    = 0
        channelid   = channel.get("id")
        displayname = channel.findall('display-name')

        if xsource.replace("'",'') == 'BDS' or len(displayname) < 4:
            displayname = displayname[0].text.encode('ascii', 'ignore').replace('\n','')
        else:
            displayname = displayname[3].text.encode('ascii', 'ignore').replace('\n','')
        if  displayname=='INDEPENDENT' or 'AFFILIATE' in displayname or displayname=='SATELLITE' or displayname=='SPORTS SATELLITE' or 'PPV' in displayname or 'SKYCUST' in displayname or 'PAID PROGRAMMING' in displayname or 'VOD ' in displayname:
            donotadd = 1

        newclean = CleanFilename(displayname)
        if newclean.endswith(' '):
            newclean = newclean[:-1]

        if not displayname in tempchans and not newclean in tempchans and not donotadd:
            writefile.write(displayname+':'+newclean+'\n')
            counter+=1
        tempchans.append(newclean)
    writefile.close()
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    dialog.ok('Rename file successfully created','A rename file has been created for %s unique %s channels. The file can be located at: [COLOR=dodgerblue]%s[/COLOR]' % (str(counter), country, os.path.join(renamefolder,xsource+'_'+country+'.ren')))
##########################################################################################
# Return a clean filename that won't cause errors
def CleanFilename(text):
    text = text.replace(' *',                  '*')
    text = text.replace(' +',                  '+')
    text = text.replace(' HDTV',                '')
    text = text.replace(' HD',                  '')
    text = text.replace(' SDTV',                '')
    text = text.replace(' SD ',                 '')
    text = text.replace(' (EAST)',              '')
    text = text.replace(' (WEST)',              '')
    text = text.replace('ROGERS ',              '')
    text = text.replace('THE SPORTS NETWORK','TSN')
    text = text.replace(' CANADA',              '')
    text = text.replace('(CANADA)',             '')
    text = text.replace('>',                    '')
    text = text.replace('_',                   ' ')

    text = re.sub('[:\\/?\<>|"]', '', text)
    text = text.strip()
    try:
        text = text.encode('ascii', 'ignore')
    except:
        text = text.decode('utf-8').encode('ascii', 'ignore')
    text = text.upper()
    return text.replace('&AMP;','&amp;')
##########################################################################################
# Remove the channel folders so we can repopulate. All mappings will be lost unless set in the master chan.xml
def rename():
    xpath = dialog.browse(1, 'Please find your xmltv file', 'files', '.xml', False, False, HOME)
    if xpath != '':
        countrylist = []
        for country in countryarray:
            countries = country[1]
            countrylist.append(countries)

        choice  = dialog.select('What country are these listings for?',countrylist)
        country = countryarray[choice][0]
        xbmc.executebuiltin("XBMC.Notification("+ADDON2.getLocalizedString(30807)+","+ADDON2.getLocalizedString(30811)+",10000,"+updateicon+")")
        xbmc.executebuiltin("ActivateWindow(busydialog)")

    # Grab the xml source, differenet sources require different methods of conversion
        with open(xpath) as myfile:
            head = str([next(myfile) for x in xrange(5)])
            xmlsource = str(re.compile('source-info-name="(.+?)"').findall(head))
            xmlsource = str(xmlsource).replace('[','').replace(']','').replace("'",'')
            xbmc.log("XML TV SOURCE: "+xmlsource)

    # Initialise the Elemettree params
        tree = Grab_XML_Tree(xpath)
    # Get root item of tree
        root         =  tree.getroot()
    # Grab all channels in XML
        channels   =  root.findall("./channel")
        channelcount =  len(channels)
        create_rename(channels,channelcount,xmlsource, country)
##########################################################################################