'''
    zen Add-on
    Copyright (C) 2016 zen

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
'''

import sys,pkgutil,re,json,urllib,urlparse,random,datetime,time,xbmcgui

from resources.lib.modules import control
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import workers

import os
from threading import Event
import xbmc
import xbmcaddon
import xbmcvfs

try: from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database

try: import xbmc
except: pass


class sources:
    def __init__(self):
        self.list = []


    def search(self, title):
        progressDialog = control.progressDialog
        progressDialog.create(control.addonInfo('name'), '')
        progressDialog.update(0,'Searching...')
        sourceDict = []
        for pkg, name, is_pkg in pkgutil.walk_packages(__path__): sourceDict.append((name, is_pkg))
        sourceDict = [i[0] for i in sourceDict if i[1] == False]
        sourceDict = [(i, __import__(i, globals(), locals(), [], -1).source()) for i in sourceDict]
        sourceDict = [i[0] for i in sourceDict]
        sourceLabel = [i for i in sourceDict]
        self.sources = []    
        threads = []			
        for source in sourceDict: threads.append(workers.Thread(self.getMovieSource, title, __import__(source, globals(), locals(), [], -1).source()))
        [i.start() for i in threads]
        timeout = 30
        string1 = "Time Elapsed %s / 30"
		
        for i in range(0, timeout * 2):
            try:
                try: info = [sourceLabel[int(re.sub('[^0-9]', '', str(x.getName()))) - 1] for x in threads if x.is_alive() == True]
                except: info = []
                
                timerange = int(i * 0.5)
                try:
                    if progressDialog.iscanceled(): break
                except:
                    pass
                try:
                    if progressDialog.iscanceled(): break
                    string4 = string1 % str(timerange)
                    string5 = str(info).translate(None, "[]'")
                    progressDialog.update(int((100 / float(len(threads))) * len([x for x in threads if x.is_alive() == False])), str(string4), str(string5))
                except:
                    pass				
				
                is_alive = [x for x in threads if x.is_alive() == True]
                if not is_alive: break
                time.sleep(0.5)
            except:
                pass
				
        for item in self.sources:	
			title = item['title']
			url = item['url'].encode('utf-8')
			mode = item['action']
			poster = item['poster']
			meta = item['meta']
			mode = item['action']
			provider = item['provider']
			if url.startswith('/'): url = "https:" + url
			label = "[I]%s[/I]  | [B]%s[/B]" % (provider, title)
			label = label.upper()
			control.addDirMeta(label,url, mode, poster, control.fanart, meta)
        


    def getMovieSource(self, title, call):
        try:
            sources = []
            sources = call.search(title)
            if sources == None: raise Exception()
            self.sources.extend(sources)
        except:
            pass




