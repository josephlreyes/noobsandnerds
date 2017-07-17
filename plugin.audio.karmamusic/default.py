import urllib,urllib2,re,xbmcplugin,xbmcgui,sys,xbmc,xbmcaddon,os,urlparse,random
import threading
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import workers
from BeautifulSoup import BeautifulSoup as bs
addon_id = 'plugin.audio.karmamusic'
fanart = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))
icon = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
HOME         =  xbmc.translatePath('special://home/')
base_url = "https://www.yourmusics.me"
artwork = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'resources/artwork/'))
ADDONPATH         =  xbmc.translatePath('special://home/userdata/addon_data/')
TempInfo = xbmc.translatePath(os.path.join(ADDONPATH + addon_id, 'tempinfo.txt'))
dialog = xbmcgui.Dialog()
def CATEGORIES():
	addDir('Artists',base_url + "/artist.html",2,artwork + "artists.png",fanart)
	addDir('Albums',base_url + "/album.html",3,artwork + "albums.png",artwork + "albums.jpg")
	addDir('Search',base_url + "/album.html",4,artwork + "search.png",artwork + "search.jpg")
	
def Artists_Menu(url):
	addDir('Most Popular',base_url + "/artist.html",21,artwork + "artists.png",fanart)
	addDir('Featured Artist',base_url + "/artist/featured.html",21,artwork + "artists.png",fanart)
	addDir('Popular In Weekly',base_url + "/artist/week.html",21,artwork + "artists.png",fanart)
	addDir('Most User Liked',base_url + "/artist/liked.html",21,artwork + "artists.png",fanart)
	addDir('By Letters',base_url + "/artist.html",22,artwork + "artists.png",fanart)

def Album_Menu(url):
	addDir('Latest Albums',base_url + "/album/latest.html",31,artwork + "albums.png",artwork + "albums.jpg")
	addDir('Most Popular',base_url + "/album.html",31,artwork + "albums.png",artwork + "albums.jpg")
	addDir('Popular In Weekly',base_url + "/album/week.html",31,artwork + "albums.png",artwork + "albums.jpg")
	addDir('Most User Liked',base_url + "/album/liked.html",31,artwork + "albums.png",artwork + "albums.jpg")

def Search_Menu():
	addDir('Artist',base_url + "/search/artist?keyword=",41,artwork + "search.png",artwork + "search.jpg")
	addDir('Albums',base_url + "/search/album?keyword=",42,artwork + "search.png",artwork + "search.jpg")
	addDir('Tracks',base_url + "/search/track?keyword=",43,artwork + "search.png",artwork + "search.jpg")

	
def Letters(url):
	link = client.request(url)
	for items in client.parseDOM(link, 'div', attrs = {'class': 'letter-index'}):
		match = re.compile('<a href="(.*?)">(.*?)</a>').findall(items)
		for url,title in match:
			url = base_url + url
			addDir(title,url,27,artwork + "artists.png",fanart)
def Letters_Artists(url):
	link = client.request(url)
	reg = re.compile('<div class="item"><span><a href="(.*?)" class="link">(.*?)</a></span>').findall(link)
	try:
		for url,title in reg:
			url = base_url + url
			title = client.replaceHTMLCodes(title)	
			addDir(title,url,23,artwork + "artists.png",fanart)	
	except:
		pass
				
def Letters_Albums(url):
	link = client.request(url)
	for items in client.parseDOM(link, 'div', attrs = {'class': 'letter-index'}):
		match = re.compile('<a href="(.*?)">(.*?)</a>').findall(items)
		for url,title in match:
			url = base_url + url
			addDir(title,url,2,icon,fanart)

def Artist_Page(url):
	link = client.request(url)
	match = re.compile('<a href="(.*?)" class="hot"><img src="(.*?)" /><em>(.*?)</em>').findall(link)
	for url,img,title in match:
		url = base_url + url
		addDir(title,url,23,img,fanart)
			
def Album_Page(url):
	link = client.request(url)
	match = re.compile('<a href="(.*?)" class="hot"><img src="(.*?)" /><em>(.*?)</em>').findall(link)
	for url,img,title in match:
		url = base_url + url
		addDir(title,url,101,img,fanart)	

def Artist_Info(iconimage, url):
	link = client.request(url)
	icon = iconimage
	for items in client.parseDOM(link, 'div', attrs = {'class': 'artist-nav'}):
		match = re.compile('href="([^"]+)">(.*?)</a>').findall(items)
		match2 = re.compile('href="([^"]+)" class=".*?">(.*?)</a>').findall(items)
		for url,title in match + match2:
			url = base_url + url
			print('ARTIST INFO', url)
			if not "overview" in title.lower():
				if "/artist/biography/" in url:
					addLink(title,url,24,artwork + "artists.png",fanart)
				if "/artist/albums/" in url:
					addDir(title,url,25,artwork + "artists.png",fanart)
				if "/artist/tracks/" in url:
					addDir(title,url,101,artwork + "artists.png",fanart)
				
def Artist_Bio(iconimage, url):
	link = client.request(url)
	icon = iconimage
	text = client.parseDOM(link, 'div', attrs = {'class': 'overview'})
	text = text[0]
	text = client.replaceHTMLCodes(text)

	text = text.encode('utf-8')
	print ("ARTIST BIO",text)
	set_text(text)

	
def Artist_Albums(iconimage, url):
	link = client.request(url)
	icon = iconimage
	soup=bs(link)
	r=soup.find('div',{'class':'artist-album'})
	reg = re.compile('<a href="(.*?)"><img src="(.*?)" alt="(.*?)"')
	result = re.findall(reg,str(r))
	for url,img,title in result:
		url = base_url + url
		title = client.replaceHTMLCodes(title)
		addDir(title,url,101,img,fanart)
		
def Artist_Tracks(name,url,iconimage):
	link = client.request(url)
	icon = iconimage
	soup=bs(link)
	r=soup.find('div',{'class':'artist-songs'})
	reg = re.compile('<div class="song-name"><a href="([^"]+)">(.*?)</a></div>')
	result = re.findall(reg,str(r))
	for url,title in result:
		url = re.sub('/track/','/download/', url)
		url = base_url + url
		title = client.replaceHTMLCodes(title)
		print('TRACKS',url)
		addLink(title,url,100,icon,fanart)	
		
def Albums(url):
	link = client.request(url)
	soup=bs(link)
	r=soup.find('div',{'class':'albums'})
	reg = re.compile('<a href="(.*?)"><img src="(.*?)" alt="(.*?)"')
	result = re.findall(reg,str(r))
	for url,img,title in result:
		url = base_url + url
		title = client.replaceHTMLCodes(title)
		addDir(title,url,101,img,fanart)


def cleanHex(text):
    def fixup(m):
        text = m.group(0)
        if text[:3] == "&#x": return unichr(int(text[3:-1], 16)).encode('utf-8')
        else: return unichr(int(text[2:-1])).encode('utf-8')
    return re.sub("(?i)&#\w+;", fixup, text.decode('ISO-8859-1').encode('utf-8'))

def get_params():
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

##################### SEARCH ################################	
def SEARCH_ARTIST(url):

	search_entered =''
	keyboard = xbmc.Keyboard(search_entered, 'Search Artist Name')
	keyboard.doModal()
	if keyboard.isConfirmed(): search_entered = keyboard.getText()
	if len(search_entered)>1:
		url = url + urllib.quote_plus(search_entered)
		link = client.request(url)
		soup=bs(link)
		r=soup.find('div',{'class':'search-artist'})
		reg = re.compile('<a href="(.*?)"><img src="(.*?)" alt="(.*?)"')
		result = re.findall(reg,str(r))
		for url,img,title in result:
			url = base_url + url
			title = client.replaceHTMLCodes(title)
			addDir(title,url,23,img,fanart)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def SEARCH_ALBUMS(url):

	search_entered =''
	keyboard = xbmc.Keyboard(search_entered, 'Search Albums')
	keyboard.doModal()
	if keyboard.isConfirmed(): search_entered = keyboard.getText()
	if len(search_entered)>1:
		url = url + urllib.quote_plus(search_entered)
		link = client.request(url)
		soup=bs(link)
		r=soup.find('div',{'class':'search-album'})
		reg = re.compile('<a href="(.*?)"><img src="(.*?)" alt="(.*?)"')
		result = re.findall(reg,str(r))
		for url,img,title in result:
			url = base_url + url
			title = client.replaceHTMLCodes(title)
			addDir(title,url,101,img,fanart)			
	xbmcplugin.endOfDirectory(int(sys.argv[1]))
	
def SEARCH_TRACKS(url):

	search_entered =''
	keyboard = xbmc.Keyboard(search_entered, 'Search Tracks')
	keyboard.doModal()
	if keyboard.isConfirmed(): search_entered = keyboard.getText()
	if len(search_entered)>1:
		url = url + urllib.quote_plus(search_entered)
		link = client.request(url)
		soup=bs(link)
		r=soup.find('div',{'class':'search-songs'})
		reg = re.compile('<div class="song-name"><a href="(.*?)" title="(.*?)">')
		result = re.findall(reg,str(r))
		for url,title in result:
			title = client.replaceHTMLCodes(title)
			url = re.sub('/track/','/download/', url)
			url = base_url + url
			print('TRACKS',url)
			title = client.replaceHTMLCodes(title)
			addLink(title,url,100,icon,fanart)	
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

	
	
################ PLAYERS ###########################
def Choose_Menu(name,url,iconimage):
		img = iconimage
		album_icon = iconimage
		print ("ALBUM ICON", album_icon)
		addLink('Play All',url,102,img,fanart)
		addDir('Browse',url,26,img,fanart)
		
			
def PLAY_FULL(name,url,iconimage):
			albumlist = []
			link = client.request(url)
			soup=bs(link)
			threads = []
			album_icon = iconimage
			print ("ALBUM ICON", album_icon)
			r=soup.find('div',{'class':'artist-songs'})
			global count
			
			reg = re.compile('<div class="song-name"><a href="([^"]+)">(.*?)</a></div>')
			result = re.findall(reg,str(r))
			count=0
 			playlist = xbmc.PlayList(0)
			playlist.clear()
			progressDialog = control.progressDialog
			progressDialog.create('Karma', '')
			progressDialog.update(0)
			for url,title in result:
				if progressDialog.iscanceled(): break
				count+=1
				url = re.sub('/track/','/download/', url)
				url = base_url + url
				title = client.replaceHTMLCodes(title)
				progress = (float(count) / float(len(result))) * 100
				progressDialog.update(int(progress), 'Retrieving and Checking Songs...', title)
				w = workers.Thread(fetch_album, url, title, album_icon)
				w.start()
				w.join()
			xbmc.Player().play( playlist )
				 

def fetch_album(url,title,album_icon):
				playlist = xbmc.PlayList(0)
				image = album_icon
				try:	
					link = client.request(url)
					match = re.findall("var url\s+=\s+'(.*?)';", link)
					matchhq = re.findall("var hqurl\s+=\s+'(.*?)';", link)	
					if control.setting('mp3bitrate') == '1':					
						try:
							print('BITRATE', control.setting('mp3bitrate'))
							if matchhq:
								url = matchhq[0]
								# print ("PLAYER TRACK", url)
								liz = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image, path=url)
								liz.setInfo('music', {'Title':title})
								liz.setProperty('IsPlayable','true')
								playlist.add( url=url, listitem=liz )
							elif match:
								url = match[0]
								print ("PLAYER TRACK", url)
								liz = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image, path=url)
								liz.setInfo('music', {'Title':title})
								liz.setProperty('IsPlayable','true')							
								playlist.add( url=url, listitem=liz )
						except:
							pass
						
					elif control.setting('mp3bitrate') == '0':
						try:
							print('BITRATE', control.setting('mp3bitrate'))
							if match:
								url = match[0]
								# print ("PLAYER TRACK", url)
								liz = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image, path=url)
								liz.setInfo('music', {'Title':title})
								liz.setProperty('IsPlayable','true')							
								playlist.add( url=url, listitem=liz )
							elif matchhq:
								url = matchhq[0]
								print ("PLAYER TRACK", url)
								liz = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image, path=url)
								liz.setInfo('music', {'Title':title})
								liz.setProperty('IsPlayable','true')
								playlist.add( url=url, listitem=liz )
						except:
							pass
				except:
					pass

			
def PLAY(name,url,iconimage):
			link = client.request(url)
			match = re.findall("var url\s+=\s+'(.*?)';", link)
			matchhq = re.findall("var hqurl\s+=\s+'(.*?)';", link)
			if control.setting('mp3bitrate') == '1':
				try:
					if matchhq:
						url = matchhq[0]
						print ("PLAYER TRACK", url)
						liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage, path=url)
						liz.setInfo('music', {'Title':name})
						liz.setProperty('IsPlayable','true')
						xbmc.Player ().play(url,liz,False)
					elif match:
						url = match[0]
						print ("PLAYER TRACK", url)
						liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage, path=url)
						liz.setInfo('music', {'Title':name})
						liz.setProperty('IsPlayable','true')
						xbmc.Player ().play(url,liz,False)
				except:
					pass
			elif control.setting('mp3bitrate') == '0':
				try:
					if match:
						url = match[0]
						print ("PLAYER TRACK", url)
						liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage, path=url)
						liz.setInfo('music', {'Title':name})
						liz.setProperty('IsPlayable','true')
						xbmc.Player ().play(url,liz,False)
					elif matchhq:
						url = matchhq[0]
						print ("PLAYER TRACK", url)
						liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage, path=url)
						liz.setInfo('music', {'Title':name})
						liz.setProperty('IsPlayable','true')
						xbmc.Player ().play(url,liz,False)
				except:
					pass
			xbmcplugin.endOfDirectory(int(sys.argv[1]))

	
def addDir(name,url,mode,iconimage,fanart,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Music", infoLabels={ "Title": name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
def addLink(name,url,mode,iconimage,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+str(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok

def set_text(text):
		file = open(TempInfo, "w")
		file.write(text)
		file.close()
		file = open(TempInfo, 'r')
		text = file.read()

		id = 10147
		xbmc.executebuiltin('ActivateWindow(%d)' % id)
		xbmc.sleep(500)
		win = xbmcgui.Window(id)
		retry = 50
		while (retry > 0):
			try:
				xbmc.sleep(10)
				retry -= 1
				win.getControl(1).setLabel('INFO:')
				win.getControl(5).setText(text)
				return
			except:
				pass
			
####### SCRAPING TOOLS #####			
def regex_get_all(text, start_with, end_with):
    r = re.findall("(?i)(" + start_with + "[\S\s]+?" + end_with + ")", text)
    return r				
def regex_from_to(text, from_string, to_string, excluding=True):
    if excluding:
	   try: r = re.search("(?i)" + from_string + "([\S\s]+?)" + to_string, text).group(1)
	   except: r = ''
    else:
       try: r = re.search("(?i)(" + from_string + "[\S\s]+?" + to_string + ")", text).group(1)
       except: r = ''
    return r        
####### PARSEDOM THX TO TKNORRIS #####

def _getDOMContent(html, name, match, ret):
    end_str = "</%s" % (name)
    start_str = '<%s' % (name)

    start = html.find(match)
    end = html.find(end_str, start)
    pos = html.find(start_str, start + 1)

    while pos < end and pos != -1:  # Ignore too early </endstr> return
        tend = html.find(end_str, end + len(end_str))
        if tend != -1:
            end = tend
        pos = html.find(start_str, pos + 1)

    if start == -1 and end == -1:
        result = ''
    elif start > -1 and end > -1:
        result = html[start + len(match):end]
    elif end > -1:
        result = html[:end]
    elif start > -1:
        result = html[start + len(match):]
    else:
        result = ''

    if ret:
        endstr = html[end:html.find(">", html.find(end_str)) + 1]
        result = match + result + endstr

    return result

def _getDOMAttributes(match, name, ret):
    pattern = '''<%s[^>]* %s\s*=\s*(?:(['"])(.*?)\\1|([^'"].*?)(?:>|\s))''' % (name, ret)
    results = re.findall(pattern, match, re.I | re.M | re.S)
    return [result[1] if result[1] else result[2] for result in results]

def _getDOMElements(item, name, attrs):
    if not attrs:
        pattern = '(<%s(?: [^>]*>|/?>))' % (name)
        this_list = re.findall(pattern, item, re.M | re.S | re.I)
    else:
        last_list = None
        for key in attrs:
            pattern = '''(<%s [^>]*%s=['"]%s['"][^>]*>)''' % (name, key, attrs[key])
            this_list = re.findall(pattern, item, re.M | re. S | re.I)
            if not this_list and ' ' not in attrs[key]:
                pattern = '''(<%s [^>]*%s=%s[^>]*>)''' % (name, key, attrs[key])
                this_list = re.findall(pattern, item, re.M | re. S | re.I)
    
            if last_list is None:
                last_list = this_list
            else:
                last_list = [item for item in this_list if item in last_list]
        this_list = last_list
    
    return this_list

def parse_dom(html, name='', attrs=None, ret=False):
    if attrs is None: attrs = {}
    if isinstance(html, str):
        try:
            html = [html.decode("utf-8")]  # Replace with chardet thingy
        except:
            print "none"
            try:
                html = [html.decode("utf-8", "replace")]
            except:
                
                html = [html]
    elif isinstance(html, unicode):
        html = [html]
    elif not isinstance(html, list):
        
        return ''

    if not name.strip():
        
        return ''
    
    if not isinstance(attrs, dict):
        
        return ''

    ret_lst = []
    for item in html:
        for match in re.findall('(<[^>]*\n[^>]*>)', item):
            item = item.replace(match, match.replace('\n', ' ').replace('\r', ' '))

        lst = _getDOMElements(item, name, attrs)

        if isinstance(ret, str):
            lst2 = []
            for match in lst:
                lst2 += _getDOMAttributes(match, name, ret)
            lst = lst2
        else:
            lst2 = []
            for match in lst:
                temp = _getDOMContent(item, name, match, ret).strip()
                item = item[item.find(temp, item.find(match)):]
                lst2.append(temp)
            lst = lst2
        ret_lst += lst

    # log_utils.log("Done: " + repr(ret_lst), xbmc.LOGDEBUG)
    return ret_lst

##### OPEN URL ######	
def open_url(url):
        # url=url.replace(' ','%20')
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
def setView(content, viewType):
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if selfAddon.getSetting('auto-view')=='true':
        xbmc.executebuiltin("Container.SetViewMode(%s)" % selfAddon.getSetting(viewType) )
		
params=get_params(); url=None; name=None; mode=None; site=None; iconimage=None
try: site=urllib.unquote_plus(params["site"])
except: pass
try: url=urllib.unquote_plus(params["url"])
except: pass
try: name=urllib.unquote_plus(params["name"])
except: pass
try: mode=int(params["mode"])
except: pass
try: iconimage=urllib.unquote_plus(params["iconimage"])
except: pass
print "Site: "+str(site); print "Mode: "+str(mode); print "URL: "+str(url); print "Name: "+str(name)
print params

if mode==None or url==None or len(url)<1: CATEGORIES()
elif mode==2: Artists_Menu(url)
elif mode==21: Artist_Page(url)
elif mode==22: Letters(url)
elif mode==23: Artist_Info(iconimage,url)
elif mode==24: Artist_Bio(iconimage,url)
elif mode==25: Artist_Albums(iconimage, url)
elif mode==26: Artist_Tracks(name,url,iconimage)
elif mode==27: Letters_Artists(url)
elif mode==3: Album_Menu(url)
elif mode==31: Albums(url)

elif mode==4: Search_Menu()
elif mode==41: SEARCH_ARTIST(url)
elif mode==42: SEARCH_ALBUMS(url)
elif mode==43: SEARCH_TRACKS(url)

elif mode==100: PLAY(name,url,iconimage)
elif mode==101: Choose_Menu(name,url,iconimage)
elif mode==102: PLAY_FULL(name,url,iconimage)

xbmcplugin.endOfDirectory(int(sys.argv[1]))

