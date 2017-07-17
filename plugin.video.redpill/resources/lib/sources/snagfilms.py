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
		
        self.name = 'SnagFilm'

        self.base_link = 'http://www.snagfilms.com'
        self.search_link = '/apis/search.json?searchTerm=%s'

    def get(self):
        r = urlparse.urljoin(self.base_link, "/categories/")
        r = client.request(r)
        r = BeautifulSoup(r)
        r = r.findAll('div', attrs = {'class': re.compile('snag-slider-item\s*')})
        for items in r:
			try:
				url = items['data-permalink'].encode('utf-8')
				title = items['data-title'].encode('utf-8')
				img = items.findAll('img')[0]['src'].encode('utf-8')
				url = urlparse.urljoin(self.base_link, url)
				control.addDir(title,url,'snagfilms_cat',img,control.fanart)
			except:
				pass

    def popular(self, url):
        r = client.request(url)
        r = client.parseDOM(r, 'div', attrs = {'class': 'doc'})
        for items in r:
                try:
					href = client.parseDOM(items, 'a', ret='href')[0].encode('utf-8')
					title = client.parseDOM(items, 'a', ret='title')[0].encode('utf-8')
					img = client.parseDOM(items, 'img', ret='src')[0].encode('utf-8')
					if img == '' or img == None: img = client.parseDOM(items, 'img', ret='data-src')[0].encode('utf-8')
					href = urlparse.urljoin(self.base_link, href)
					img = urlparse.urljoin(self.base_link, img)
					meta = {"poster": img , "title" : title}
					meta = urllib.quote_plus(json.dumps(meta))
					control.addDirMeta(title,href,'snagfilms_resolve', img, control.fanart, meta)
                except:
					pass
					
		
    def cat(self, url):
        try:
			r = urlparse.urljoin(self.base_link, url)
			r = client.request(r)
			r = BeautifulSoup(r)
			
			r = r.findAll('div', attrs = {'class': re.compile('snag-slider-item\s*')})
			for items in r:
				try:
					href = items['data-permalink'].encode('utf-8')
					title = items['data-title'].encode('utf-8')
					img = items.findAll('img')[0]['src'].encode('utf-8')
					if img == '' or img == None: img = items.findAll('img')[0]['data-src'].encode('utf-8')
					href = urlparse.urljoin(self.base_link, href)
					meta = {"poster": img , "title" : title}
					meta = urllib.quote_plus(json.dumps(meta))
					control.addDirMeta(title,href,'snagfilms_resolve', img, control.fanart, meta)
				except:
					pass
				
        except:
			pass
			


    def resolve(self, url, title, iconimage, meta):
        r = client.request(url)
        r = BeautifulSoup(r)
        r = r.findAll('div', attrs = {'class': 'film-container'})
        for frame in r:
			url = frame.findAll('iframe')[0]['src'].encode('utf-8')
			if "embed/player" in url.lower():
				url = urlparse.urljoin(self.base_link, url)
				try:host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
				except: host = 'Unknown'
				s = client.request(url)
				s = re.findall('src:\s*"(.+?)"', s)[-1]
				url = s.encode('utf-8')
				if ".mp4?" in url: 
					url = url.split('.mp4?')[0]
					url = url + ".mp4"
				url = url + "|directplay" 
				print ("SNAGFILMS URL", url)
				
				control.addLink(host,url,'play', iconimage, control.fanart, meta)	


			
#-------------------------- GLOBAL --------------------------------------------

    def search(self, title):
        sources = []

        query = self.search_link % title
        query = urlparse.urljoin(self.base_link, query)
        r = client.request(query, XHR=True)
        r = json.loads(r)
        results = r['results']
        for items in results:
			title = items['title'].encode('utf-8')
			url = items['permalink'].encode('utf-8')
			img = items['imageUrl'].encode('utf-8')
			url = urlparse.urljoin(self.base_link, url)
			meta = {"poster": img , "title" : title}
			meta = urllib.quote_plus(json.dumps(meta))

			sources.append({'title': title, 'provider': self.name, 'url': url, 'poster': img, 'meta':meta, 'action':'snagfilms_resolve'})
        return sources		
			
