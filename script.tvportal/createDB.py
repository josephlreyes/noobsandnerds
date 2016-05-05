# TV Portal EPG Converter
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
import time, datetime, re, shutil, csv, hashlib
import dixie, sfile, download
import calendar as cal
import xml.etree.ElementTree as ET

from sqlite3 import dbapi2 as sqlite
from time import mktime

import sys, traceback

# Global variables
AddonID     =  'script.tvportal'
ADDON       =  xbmcaddon.Addon(id=AddonID)
ADDONS      =  xbmc.translatePath('special://home/addons/')
USERDATA    =  xbmc.translatePath('special://profile/')
ADDON_DATA  =  xbmc.translatePath(os.path.join(USERDATA,'addon_data'))
dbpath      =  xbmc.translatePath(os.path.join(ADDON_DATA,AddonID,'program.db'))
dialog      =  xbmcgui.Dialog()
dp          =  xbmcgui.DialogProgress()
updateicon  =  os.path.join(ADDONS,AddonID,'resources','update.png')
chanxmlfile =  os.path.join(ADDON_DATA,AddonID,'chan.xml')
catsxfile   =  os.path.join(ADDON_DATA,AddonID,'cats.xml')
xmlmaster   =  os.path.join(ADDONS,AddonID,'resources','chan.xml')
catsmaster  =  os.path.join(ADDONS,AddonID,'resources','cats.xml')
csvfile     =  os.path.join(ADDON_DATA,AddonID,'programs.csv')
tempxml     =  os.path.join(ADDON_DATA,AddonID,'temp.xml')
path        =  dixie.GetChannelFolder()
chan        =  os.path.join(path, 'channels')
log_path    =  xbmc.translatePath('special://logpath/')
usenanxml   =  ADDON.getSetting('usenanxml')
stop        =  0
chanchange  =  0
catschange  =  0
errorlist   = ['none']

##########################################################################################
# Initialise the database calls
def DB_Open():
    global cur
    global con
    con = sqlite.connect(dbpath)
    cur = con.cursor()
##########################################################################################
# Clean up the database and remove stale listings
def Clean_DB():
# Set paramaters to check in db, cull = the datetime (we've set it to 12 hours in past)
    starttime = datetime.datetime.today() - datetime.timedelta(hours=12)
    cull      = int(time.mktime(starttime.timetuple()))

    DB_Open()
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    xbmc.executebuiltin("XBMC.Notification("+ADDON.getLocalizedString(30837)+","+ADDON.getLocalizedString(30838)+",5000,"+updateicon+")")
    cur.execute("DELETE FROM programs WHERE end_date < "+str(cull))
    cur.execute("VACUUM")
    con.commit()
    cur.close()
    xbmc.executebuiltin('Dialog.Close(busydialog)')
##########################################################################################
# Clear the stored xml sizes so we can force an update scan
def Wipe_XML_Sizes():
    DB_Open()
    cur.execute("DELETE FROM xmls WHERE id > 0")
    cur.execute("VACUUM")
    con.commit()
    cur.close()
##########################################################################################
## Function to open a URL
def Open_URL(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link     = response.read()
    response.close()
    return link
##########################################################################################
# Check if the online file date has changed
def Check_Date(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    conn = urllib2.urlopen(req)
    last_modified = conn.info().getdate('last-modified')
    last_modified = time.strftime('%Y%m%d%H%M%S', last_modified)
    dixie.log("Last modified: "+last_modified)
    return last_modified
##########################################################################################
# Grab XML paths and offsets
def Grab_XML_Settings(xnumber):
    isurl      = 0
    addxmltodb = 1
    xmltype    = ADDON.getSetting('xmlpath'+xnumber+'.type')
    offset     = ADDON.getSetting('offset'+xnumber)
    if xmltype == 'File':
        dixie.log("XML"+xnumber+': Local File')
        xmlpath = ADDON.getSetting('xmlpath'+xnumber+'.file')
        localcheck = hashlib.md5(open(xmlpath,'rb').read()).hexdigest()
    elif xmltype == 'URL':
        xmlpath = ADDON.getSetting('xmlpath'+xnumber+'.url')
        dixie.log("XML"+xnumber+': URL')
        localcheck = Check_Date(xmlpath)
    else:
        dixie.log("XML"+xnumber+': None')
        addxmltodb = 0
        return "None"
    if addxmltodb:
# Try to access the db, if it's locked we wait 5s and try again
        try:
            DB_Open()
            cur.execute("SELECT COUNT(*) from xmls where id LIKE '"+xnumber+"';")
            data = cur.fetchone()[0]
            if data:
                cur.execute("SELECT size FROM xmls WHERE id=?", (xnumber,))
                newdata = str(cur.fetchone()[0])
                dixie.log('Existing entry size: '+str(newdata))
                if newdata != localcheck:
#                dixie.log('Updating XML'+xnumber+' size in db to '+localcheck)
#                cur.execute("update xmls set size='"+localcheck+"' where id LIKE '"+xnumber+"';")
                    if xmltype == 'URL':
                        isurl = 1
                else:
                    dixie.log('No change in XML'+xnumber+' so no need to update')
                    addxmltodb = 0
            else:
#            dixie.log('Adding XML'+xnumber+' size to db - '+localcheck)
#            cur.execute("insert into xmls (id, size) values ('"+xnumber+"','"+localcheck+"');")
                if xmltype == 'URL':
                    isurl = 1
            cur.close()
            con.close()
        except:
            xbmc.sleep(5000)
            Grab_XML_Settings(xnumber)

        if addxmltodb == 1:
            Start(xmlpath,offset,isurl)
            if data and newdata != localcheck:
                DB_Open()
                dixie.log('Updating XML'+xnumber+' size in db to '+localcheck)
                cur.execute("update xmls set size='"+localcheck+"' where id LIKE '"+xnumber+"';")
            else:
                DB_Open()
                dixie.log('Adding XML'+xnumber+' size to db - '+localcheck)
                cur.execute("insert into xmls (id, size) values ('"+xnumber+"','"+localcheck+"');")
            con.commit()
            cur.close()
            con.close()

##########################################################################################
# Return the last error
def Last_Error():
    errorstring = traceback.format_exc()
    dixie.log("ERROR: "+errorstring)
    errorlinematch  = re.compile(': line (.+?),').findall(errorstring)
    errormatch      = errorlinematch[0] if (len(errorlinematch) > 0) else ''
    return errormatch
##########################################################################################
# Function to convert timestamp into proper integer that can be used for schedules
def Time_Convert(starttime,xsource,offset):
# Split the time from the string that also contains the time difference
    starttime, diff  = starttime.split(' ')

    year             = starttime[:4]
    month            = starttime[4:6]
    day              = starttime[6:8]
    hour             = starttime[8:10]
    minute           = starttime[10:12]
    secs             = starttime[12:14]

# Convert the time diff factor into an integer we can work with
    if xsource == "'zap2it.com'":
        diff         = int(diff[:-2])-1+int(offset) # The -1 is to bring in line with BST
    else:
        diff         = int(diff[:-2])+1+int(offset) # The +1 is to convert from UTC format
    starttime        = datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),int(secs))
    starttime        = starttime + datetime.timedelta(hours=diff)
    starttime        = time.mktime(starttime.timetuple())

    return int(starttime)
##########################################################################################
# Check if item already exists in database
def updateDB(chan, s_date):
    entryexists = 0

# Changed start_date from = to LIKE (03.05.16)
    cur.execute('select channel, start_date from programs where channel LIKE "'+chan+'" and start_date LIKE "'+s_date+'";')
    try:
        row = cur.fetchone()
        if row:
            return True
    except:
        return False
##########################################################################################
# Work out how many days worth of guides we have available
def Get_Dates():
    DB_Open()
    emptydb  = 0
    datelist = []
    cur.execute("SELECT MIN(start_date) FROM programs;")
    mindate  = cur.fetchone()[0]

    mindate = datetime.datetime.fromtimestamp(mindate)
    year1   = str(mindate)[:4]
    month1  = str(mindate)[5:7]
    day1    = str(mindate)[8:10]


    cur.execute("SELECT MAX(start_date) FROM programs;")
    maxdate = cur.fetchone()[0]
    dixie.log("maxdate: "+str(maxdate))

    maxdate = datetime.datetime.fromtimestamp(maxdate)
    year2   = str(maxdate)[:4]
    month2  = str(maxdate)[5:7]
    day2    = str(maxdate)[8:10]

    d1      = datetime.date(int(year1), int(month1), int(day1))
    d2      = datetime.date(int(year2), int(month2), int(day2))
    diff    = d2 - d1
    dixie.log("Successfully grabbed dates, now inserting into db")

# Grab the time now so we can update the db with timestamp
    nowtime     = cal.timegm(datetime.datetime.timetuple(datetime.datetime.now()))
    cleantime   = str(nowtime)

# Insert our dates into the db so the epg can scroll forward in time
    for i in range(diff.days + 1):
        newdate = (d1 + datetime.timedelta(i)).isoformat()
        cur.execute("SELECT COUNT(*) from updates where date LIKE '"+newdate+"';")
        data = cur.fetchone()[0]
        if data:
            dixie.log("Attempting to update records for: "+str(newdate))
            cur.execute('update updates set source=?, date=?, programs_updated=? where date LIKE "'+str(newdate)+'";', ['dixie.ALL CHANNELS',str(newdate),cleantime])
            con.commit()
            dixie.log("Successfully updated rows")
        else:
            dixie.log("New date in db, lets create new entries")
            cur.execute("insert into updates (source, date, programs_updated) values (?, ?, ?)", ['dixie.ALL CHANNELS',str(newdate),cleantime] )
            con.commit()
            dixie.log("Successfully inserted rows")
    cur.close()
    con.close()
##########################################################################################
# Attempt to fix badly formed XML files with special characters in
def Fix_XML(errorline):
    dixie.log("FIX_XML Function started")
    counter = 1
    rawfile = open(xmlpath,"r")
    lines = rawfile.readlines()
    rawfile.close()

    newfile = open(xmlpath,'w')
    for line in lines:
        counterstr = str(counter)
        if counterstr == errorline:
            dixie.log("Removing Line "+counterstr)
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
            dixie.log("Badly formed XML file, trying to fix...")
#            traceback.print_exc()
            traceerror = Last_Error()
            dixie.log("Error List: "+str(errorlist))
            dixie.log("Current Error: "+str(traceerror))
            dixie.log("Error -1: "+errorlist[-1])
            if traceerror == errorlist[-1]:
                dixie.log("Error matched one in array, lets stop the while loop")
                tree = ET.parse(xmlpath)
                stop = 1
            else:
                dixie.log("New error, adding to array: "+traceerror)
                errorlist.append(traceerror)
                dialog.ok('Badly Formed XML File','You have an error on line [COLOR=dodgerblue]'+str(traceerror)+'[/COLOR] of your XML file. Press OK to continue scanning, we will then try and fix any errors.')
                Fix_XML(traceerror)
    return tree
##########################################################################################
# Create CSV for import and update chan.xml and cats.xml
def Create_CSV(channels,channelcount,listingcount,programmes,xsource,offset):
    listpercent =  1
    listcount   =  1
    mode        =  1
    if os.path.exists(dbpath):
        mode = 2
    try:
        os.remove(os.path.join(ADDON_DATA, AddonID, 'settings.cfg'))
    except:
        dixie.log("No settings.cfg file to remove")
    xbmc.executebuiltin("Dialog.Close(busydialog)")

# Read main chan.xml into memory so we can add any new channels
    if not os.path.exists(chanxmlfile):
        writefile   = open(chanxmlfile,'w+')
        writefile.write('<?xml version="1.0" encoding="UTF-8"?>\n<tv>\n</tv>\n')
        writefile.close()

    chanxml     =  open(chanxmlfile,'r')
    content     = chanxml.read()
    chanxml.close()

    writefile   = open(chanxmlfile,'w+')
    replacefile = content.replace('</tv>','')
    writefile.write(replacefile)
    writefile.close()
    writefile   = open(chanxmlfile,'a')

# Read cats.xml into memory so we can add any new channels
    catsxml     = open(os.path.join(ADDON_DATA,AddonID,'cats.xml'),'r')
    content2    = catsxml.read()
    catsxml.close()

    writefile2  = open(os.path.join(ADDON_DATA,AddonID,'cats.xml'),'w+')
    replacefile = content2.replace('</Document>','')
    writefile2.write(replacefile)
    writefile2.close()
    writefile2  = open(os.path.join(ADDON_DATA,AddonID,'cats.xml'),'a')

# Set a temporary list matching channel id with real name
    dixie.log("Creating List of channels")
    tempchans    = []
    dixie.log("Channels Found: "+str(channelcount))
    xbmc.executebuiltin("XBMC.Notification("+ADDON.getLocalizedString(30816)+str(channelcount)+","+ADDON.getLocalizedString(30812)+",10000,"+updateicon+")")
    for channel in channels:
        channelid   = channel.get("id")
        displayname = channel.findall('display-name')
        if len(displayname) > 3 and displayname[3]!='Independent' and not 'Affiliate' in displayname[3] and displayname[3]!='Satellite' and displayname[3]!='Sports Satellite' :
            displayname = displayname[3].text.encode('ascii', 'ignore').replace('&','&amp;').replace("'",'').replace(",",'').replace(".",'')
        else:
            displayname = displayname[0].text.encode('ascii', 'ignore').replace('&','&amp;').replace("'",'').replace(",",'').replace(".",'')

        if displayname in tempchans:
            displayname  = 'donotadd'

        if not displayname in tempchans:
# Add channel to chan.xml file
            if not '<channel id="'+str(displayname)+'">' in content:
                writefile.write('  <channel id="'+displayname+'">\n    <display-name lang="en">'+displayname+'</display-name>\n  </channel>\n')
# Add channel to cats.xml file
            if not '<channel>'+str(displayname)+'</channel>' in content2:
                writefile2.write(' <cats>\n    <category>Uncategorised</category>\n    <channel>'+displayname+'</channel>\n </cats>\n')
            tempchans.append([channelid,displayname])
        else:
            dixie.log("### Duplicate channel - skipping "+str(displayname))


    writefile.write('</tv>')
    writefile.close()
    writefile2.write('</Document>')
    writefile2.close()

# Loop through and grab each channel listing and add to array
    xbmc.executebuiltin("XBMC.Notification("+ADDON.getLocalizedString(30815)+","+ADDON.getLocalizedString(30812)+",10000,"+updateicon+")")
    currentlist  = []
    dixie.log("Total Listings to scan in: "+str(listingcount))
    xbmc.executebuiltin("XBMC.Notification("+ADDON.getLocalizedString(30818)+"[COLOR=dodgerblue]"+str(listingcount)+"[/COLOR],"+ADDON.getLocalizedString(30812)+",10000,"+updateicon+")")
    writetofile = open(csvfile,'w+')
    dp.create('Converting XML','','Please wait...','')
    writetofile.write('channel,title,start_date,end_date,description,image_large,image_small,source,subTitle')
    for programme in programmes:
#        try:
        icon = 'special://home/addons/'+AddonID+'/resources/dummy.png'
        starttime  = programme.get("start")
        starttime2 = Time_Convert(starttime,xsource,offset)
        endtime    = programme.get("stop")
        endtime2   = Time_Convert(endtime,xsource,offset)
        channel    = programme.get("channel").encode('ascii', 'ignore')
        try:
            title  = programme.find('title').text.encode('ascii', 'ignore').replace(',','.').replace('"','&quot;')
        except:
            title = "No information available"
        try:
            subtitle = programme.find('sub-title').text.encode('ascii', 'ignore').replace(',','.').replace('"','&quot;')
        except:
            subtitle = ''
        try:
            desc = programme.findtext('desc', default='No programme information available').encode('ascii', 'ignore').replace(',','.').replace('"','&quot;')
        except:
            desc = 'No information available'
        for icon in programme.iter('icon'):
            icon = str(icon.attrib).replace("{'src': '",'').replace("'}",'').replace(',','.').replace('"','&quot;')

# Convert the channel id to real channel name
        for matching in tempchans:
            if matching[0] == channel:
                cleanchan = str(matching[1])

# Check if this already exists in the database
        if str(cleanchan)!='donotadd':
            writetofile.write('\n"'+str(cleanchan)+'","'+str(title)+'",'+str(starttime2)+','+str(endtime2)+',"'+str(desc)+'",,'+str(icon)+',dixie.ALL CHANNELS,'+subtitle+',')

        listcount += 1
        if listcount == int(listingcount/100):
            listcount = 0
            dp.update(listpercent,'','','')
            listpercent = listpercent+1

#        except:
#            try:
#                dixie.log("FAILED to pull details for item: "+str(title)+": "+str(subtitle))
#            except:
#                dixie.log("FAILED to import #"+str(listcount))
#            listcount += 1

    writetofile.close()
    Import_CSV(mode)
##########################################################################################
# Import the newly created csv file
def Import_CSV(mode):
    with open(csvfile,'rb') as fin:
        dr = csv.DictReader(fin) # comma is default delimiter
        to_db = [(i['channel'], i['title'],i['start_date'], i['end_date'], i['description'],i['image_large'], i['image_small'], i['source'], i['subTitle']) for i in dr]

    DB_Open()
    cur.executemany("INSERT INTO programs (channel,title,start_date,end_date,description,image_large,image_small,source,subTitle) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)
    con.commit()
    cur.execute("DELETE FROM programs WHERE RowID NOT IN (SELECT MIN(RowID) FROM programs GROUP BY channel,start_date,end_date);")
    con.commit()
    cur.close()
    con.close()

# Insert relevant records into the updates table, if we don't do this we can't move forward in time in the EPG
    Get_Dates()
    if os.path.exists(csvfile):
        try:
            os.remove(csvfile)
        except:
            dixie.log("Unable to remove csv file, must be in use still")

    if os.path.exists(tempxml):
        try:
            os.remove(tempxml)
        except:
            dixie.log("Unable to remove temp xml file, must be in use still")

#        openepg = dialog.yesno(ADDON.getLocalizedString(30819),ADDON.getLocalizedString(30820))
#        if openepg:
#            xbmc.executebuiltin('RunAddon('+AddonID+")'")

##########################################################################################
# Remove the channel folders so we can repopulate. All mappings will be lost unless set in the master chan.xml
def Start(xpath,offset,isurl):
    stop    = 0
    dixie.log("XPATH: "+xpath)
    if not os.path.exists(catsxfile):
        shutil.copyfile(catsmaster,catsxfile)
    try:
        os.remove(os.path.join(ADDON_DATA, AddonID, 'settings.cfg'))
    except:
        dixie.log("### No settings.cfg file to remove")

# Check database isn't locked and continue if possible
    if os.path.exists(dbpath):
        try:
            os.rename(dbpath,dbpath+'1')
            os.rename(dbpath+'1',dbpath)
            dixie.log("Database not in use, we can continue")
        except:
            dixie.log("### Database in use, Kodi needs a restart, if that doesn't work you'll need to restart your system.")
            dialog.ok(ADDON.getLocalizedString(30813),ADDON.getLocalizedString(30814))
            stop = 1

    if stop == 0:
        xbmc.executebuiltin("XBMC.Notification("+ADDON.getLocalizedString(30807)+","+ADDON.getLocalizedString(30811)+",10000,"+updateicon+")")
        xbmc.executebuiltin("ActivateWindow(busydialog)")

# Grab the xml source, differenet sources require different methods of conversion
        if isurl == 1:
            dixie.log('File is URL, downloading to temp.xml')
            download.download(xpath,tempxml)
            xpath = tempxml

        with open(xpath) as myfile:
            head = str([next(myfile) for x in xrange(5)])
            xmlsource = str(re.compile('source-info-name="(.+?)"').findall(head))
            xmlsource = str(xmlsource).replace('[','').replace(']','')
            dixie.log("XML TV SOURCE: "+xmlsource)

# Initialise the Elemettree params
        tree = Grab_XML_Tree(xpath)

# Get root item of tree
        root         =  tree.getroot()

# Grab all channels in XML
        channels   =  root.findall("./channel")
        channelcount =  len(channels)

# Grab all programmes in XML
        programmes   =  root.findall("./programme")

# Get total amount of programmes
        listingcount =  len(programmes)
        xbmc.executebuiltin('Dialog.Close(busydialog)')

        try:
            cur.close()
            con.close()
        except:
            dixie.log("Database not open, we can continue")
        Create_CSV(channels,channelcount,listingcount,programmes,xmlsource,offset)
##########################################################################################
# Create the main database
def Create_DB():
    if not os.path.exists(dbpath):
        DB_Open()
        versionvalues = [1,4,0]
        try:
            cur.execute('create table programs(channel TEXT, title TEXT, start_date TIMESTAMP, end_date TIMESTAMP, description TEXT, image_large TEXT, image_small TEXT, source TEXT, subTitle TEXT);')
            con.commit()
            cur.execute('create table updates(id INTEGER, source TEXT, date TEXT, programs_updated TIMESTAMP, PRIMARY KEY(id));')
            con.commit()
            cur.execute('create table version(major INTEGER, minor INTEGER, patch INTEGER);')
            con.commit()
            cur.execute('create table xmls(id INTEGER, size INTEGER);')
            con.commit()
            cur.execute("insert into version (major, minor, patch) values (?, ?, ?);", versionvalues)
            con.commit()

        except:
            dixie.log("### Valid program.db file exists")

        cur.close()
        con.close()

############### SCRIPT STARTS HERE ###############

# Allow update to take place if set off from settings menu even if music/video is playing
dixie.log('Arg: '+sys.argv[1])
if sys.argv[1]=='normal' or sys.argv[1]=='rescan' or sys.argv[1]=='update':
    while xbmc.Player().isPlaying():
        xbmc.sleep(5000)

# Force a rescan of the channel listings
if sys.argv[1]=='rescan':
    Wipe_XML_Sizes()

if sys.argv[1]=='full':
    dixie.log('### START CHECK ###')
    dixie.log('Checking for updated listings and clearing out old data')

if usenanxml == 'true':
    if not os.path.exists(chanxmlfile):
        dixie.log("Copying chan.xml to addon_data")
        shutil.copyfile(xmlmaster, chanxmlfile)
    else:
        dixie.log("Chan.xml file already exists in addon_data")

    if not os.path.exists(catsxfile):
        dixie.log("Copying cats.xml to addon_data")
        shutil.copyfile(catsmaster, catsxfile)
    else:
        dixie.log("Cats.xml file exists in addon_data")

xbmc.executebuiltin("XBMC.Notification("+ADDON.getLocalizedString(30837)+","+ADDON.getLocalizedString(30838)+",5000,"+updateicon+")")
Create_DB()
Grab_XML_Settings('1')
Grab_XML_Settings('2')
Grab_XML_Settings('3')
Grab_XML_Settings('4')
Grab_XML_Settings('5')
if sys.argv[1]!='normal':
    Clean_DB()
    xbmc.executebuiltin("XBMC.Notification("+ADDON.getLocalizedString(30839)+","+ADDON.getLocalizedString(30840)+",5000,"+updateicon+")")
else:
    try:
        xbmc.executebuiltin('Dialog.Close(busydialog)')
    except:
        pass

if sys.argv[1]=='full':
    dixie.log('### END CHECK ###')
    dixie.log('Listings updates and database clean is complete.')
