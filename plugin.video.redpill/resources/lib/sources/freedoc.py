import urllib,urllib2,re,xbmcplugin,xbmcgui,sys,xbmc,xbmcaddon,os,urlparse,random
import threading, json
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import cleantitle
from BeautifulSoup import BeautifulSoup 
meta = {}
class source:
    def __init__(self):
        self.list = []
		
        self.name = 'FreeDoc'

        self.base_link = 'https://freedocumentaries.org'
        self.search_link = "/search?q=%s"
        print ("FREEDOC INIT")

    def get(self):

        r = client.request(self.base_link)
        r = re.compile('<h2 class="hidden-xs">Categories</h2(.+?)/ul>', re.DOTALL).findall(r)
        for items in r:
			match = re.compile('<a href="(.+?)">(.+?)<span').findall(items)
			for href, title in match:
				url = urlparse.urljoin(self.base_link, href)
				control.addDir(title,url,'freedoc_cat',control.fanart,control.fanart)

    def cat(self, url):

        r = client.request(url)
        r = BeautifulSoup(r)
        r = r.findAll('div', attrs = {'class': 'film'})
        for items in r:
			print ("FREEDOC 1", items)
			url = items.findAll('a')[0]['href'].encode('utf-8')
			img = items.findAll('img')[0]['src'].encode('utf-8')
			title = url.split('/')[-1]
			title = cleantitle.get2(title)
			url = urlparse.urljoin(self.base_link, url)
			img = urlparse.urljoin(self.base_link, img)
			meta = {"poster": img , "title" : title}
			meta = urllib.quote_plus(json.dumps(meta))
			control.addDirMeta(title,url,'freedoc_resolve', img, control.fanart, meta)


    def resolve(self, url, title, iconimage, meta):
        r = client.request(url)
        r = BeautifulSoup(r)
        r = r.findAll('iframe')
        for src in r:
			url = src['src'].encode('utf-8')
			try:host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
			except: host = 'Unknown'
			control.addLink(host,url,'play', iconimage, control.fanart, meta)	


			
#-------------------------- GLOBAL --------------------------------------------

    def search(self, title):
        sources = []
        print ("FREEDOC SEARCH", title)
        query = self.search_link % title
        query = urlparse.urljoin(self.base_link, query)
        r = client.request(query)
        r = BeautifulSoup(r)
        r = r.findAll('div', attrs = {'class': 'film'})
        for items in r:
			
			url = items.findAll('a')[0]['href'].encode('utf-8')
			img = items.findAll('img')[0]['src'].encode('utf-8')
			title = url.split('/')[-1]
			title = cleantitle.get2(title)
			url = urlparse.urljoin(self.base_link, url)
			img = urlparse.urljoin(self.base_link, img)
			meta = {"poster": img , "title" : title}
			meta = urllib.quote_plus(json.dumps(meta))

			sources.append({'title': title, 'provider': self.name, 'url': url, 'poster': img, 'meta':meta, 'action':'freedoc_resolve'})
        return sources		
			
