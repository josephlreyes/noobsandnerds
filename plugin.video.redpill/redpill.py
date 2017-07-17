import urllib,urllib2,re,xbmcplugin,xbmcgui,sys,xbmc,xbmcaddon,os,urlparse,random,json
import threading
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import workers
from BeautifulSoup import BeautifulSoup 
dialog = xbmcgui.Dialog()
url=None; name=None; mode=None; site=None; iconimage=None
addon_id = 'plugin.video.redpill'
HOME         =  xbmc.translatePath('special://home/')

def CATEGORIES():
	addDir('Snagfilms',"",'snagfilms', control.icon,control.fanart)

	addDir('Documentary Storm',"",'docstorm', control.icon,control.fanart)
	addDir('Top Documentary',"",'topdocs', control.icon,control.fanart)
	addDir('Free Documentary',"",'freedoc', control.icon,control.fanart)
	addDir('Documentary Heaven',"",'docheaven', control.icon,control.fanart)
	addDir('Search',"",'search', control.icon,control.fanart)

def Artists(url):

	r = client.request(url)
	html = BeautifulSoup(r)
	html = html.findAll('div', attrs = {'class': '"artist-letter'})
	for items in html:
		s = items.findAll('a')
		for container in s:
			title = container['title'].encode('utf-8')
			href = container['href'].encode('utf-8')
			
			addDir(title,href,'artists',artwork + "artists.png",fanart)


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
		
			

def clean_html(title):
	title = title.replace('&quot;', '\"').replace('&amp;', '&')
	title = title.replace('\\n','').replace('\\t','')
	title = title.replace('\\','')
	title = ' '.join(title.split())
	return title	
			

def addDir(name,url,mode,iconimage,fanart,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&action="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Music", infoLabels={ "Title": name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
def addLink(name,url,mode,iconimage,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&action="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+str(description)
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
			

def setView(content, viewType):
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if selfAddon.getSetting('auto-view')=='true':
        xbmc.executebuiltin("Container.SetViewMode(%s)" % selfAddon.getSetting(viewType) )
		


params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')

name = params.get('name')

title = params.get('title')

year = params.get('year')

imdb = params.get('imdb')

tvdb = params.get('tvdb')

tmdb = params.get('tmdb')

site = params.get('site')

iconimage = params.get('iconimage')

mode = params.get('mode')

premiered = params.get('premiered')

url = params.get('url')

image = params.get('image')

meta = params.get('meta')

select = params.get('select')

query = params.get('query')

source = params.get('source')

content = params.get('content')
import json
if action == None:
	CATEGORIES()
if action == 'play':
	from resources.lib.modules.player import player

	meta = json.loads(meta)
	
	print ("PLAYER META", meta)
	player().run(name, url, meta)
	
	
#------------------------ FREEDOC -----------------------------
if action == 'freedoc':
    from resources.lib.sources import freedoc
    freedoc.source().get()

if action == 'freedoc_cat':
    from resources.lib.sources import freedoc
    freedoc.source().cat(url)

if action == 'freedoc_resolve':
    from resources.lib.sources import freedoc
    freedoc.source().resolve(url, name, iconimage, meta)
#------------------------  -----------------------------	

if action == 'docheaven':
    from resources.lib.sources import docheaven
    docheaven.source().get()

if action == 'docheaven_cat':
    from resources.lib.sources import docheaven
    docheaven.source().cat(url)
	
if action == 'docheaven_popular':
    from resources.lib.sources import docheaven
    docheaven.source().popular(url)

if action == 'docheaven_resolve':
    from resources.lib.sources import docheaven
    docheaven.source().resolve(url, name, iconimage, meta)
	
#-----------------------------------------------------------------	
	
if action == 'topdocs':
    from resources.lib.sources import topdocs
    topdocs.source().get()

if action == 'topdocs_cat':
    from resources.lib.sources import topdocs
    topdocs.source().cat(url)

if action == 'topdocs_resolve':
    from resources.lib.sources import topdocs
    topdocs.source().resolve(url, name, iconimage, meta) 	
	
if action == 'topdocs_popular':
    from resources.lib.sources import topdocs
    topdocs.source().popular(url) 		
	
	
#------------------------  -----------------------------	

if action == 'docstorm':
    from resources.lib.sources import docstorm
    docstorm.source().get()

if action == 'docstorm_cat':
    from resources.lib.sources import docstorm
    docstorm.source().cat(url)
	
if action == 'docstorm_popular':
    from resources.lib.sources import docstorm
    docstorm.source().popular(url)

if action == 'docstorm_resolve':
    from resources.lib.sources import docstorm
    docstorm.source().resolve(url, name, iconimage, meta)
	
#-----------------------------------------------------------------	


#------------------------  -----------------------------	

if action == 'snagfilms':
    from resources.lib.sources import snagfilms
    snagfilms.source().get()

if action == 'snagfilms_cat':
    from resources.lib.sources import snagfilms
    snagfilms.source().cat(url)
	
if action == 'snagfilms_popular':
    from resources.lib.sources import snagfilms
    snagfilms.source().popular(url)

if action == 'snagfilms_resolve':
    from resources.lib.sources import snagfilms
    snagfilms.source().resolve(url, name, iconimage, meta)
	
#-----------------------------------------------------------------


#------------------------ SEARCH -----------------------------
if action == 'search':
	query =''
	keyboard = xbmc.Keyboard(query, 'Search Documentary')
	keyboard.doModal()
	if keyboard.isConfirmed(): query = keyboard.getText()
	if len(query)>1:
		query = urllib.quote_plus(query)
		from resources.lib.sources import sources
		sources().search(query)		
	


xbmcplugin.endOfDirectory(int(sys.argv[1]))

