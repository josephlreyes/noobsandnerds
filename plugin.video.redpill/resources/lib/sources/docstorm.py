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
		
        self.name = 'DocStorm'

        self.base_link = 'https://documentarystorm.com'
        self.search_link = '/?s=%s'

    def get(self):
	
        control.addDir('Top 100',self.base_link + '/top-100-documentary-films/','docstorm_cat',control.fanart,control.fanart)
        r = client.request(self.base_link)
        r = BeautifulSoup(r)
        r = r.findAll('li', attrs = {'class': re.compile('cat-item')})
        for items in r:
			try:
				
				u = items.findAll('a')
				for s in u:
					
					url = s['href'].encode('utf-8')
					title = s.string
					print ("DOCSTORM ITEMS", u)
					url = urlparse.urljoin(self.base_link, url)
					control.addDir(title,url,'docstorm_cat',control.fanart,control.fanart)
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
					href = urlparse.urljoin(self.base_link, href)
					img = urlparse.urljoin(self.base_link, img)
					meta = {"poster": img , "title" : title}
					meta = urllib.quote_plus(json.dumps(meta))
					control.addDirMeta(title,href,'docstorm_resolve', img, control.fanart, meta)
                except:
					pass
					

    def cat(self, url):
	
        try:

			r = client.request(url)
			query = BeautifulSoup(r)
			r = query.findAll('div', attrs = {'class': 'item'})
			for items in r:
				href = items.findAll('a')[0]['href'].encode('utf-8')
				img = items.findAll('img')[0]['src'].encode('utf-8')
				title = items.findAll('img')[0]['alt'].encode('utf-8')
				title = cleantitle.get2(title)
				href = urlparse.urljoin(self.base_link, href)
				img = urlparse.urljoin(self.base_link, img)
				meta = {"poster": img , "title" : title}
				meta = urllib.quote_plus(json.dumps(meta))
				control.addDirMeta(title,href,'docstorm_resolve', img, control.fanart, meta)
				
        except:
			pass
			
        try:
			n = query.findAll('link', attrs = {'rel': 'next'})
			for p in n:
				page = p['href'].encode('utf-8')
				page_title = page.split('/')[-1]
				if page_title == '': page_title = '1'
				page = urlparse.urljoin(self.base_link, page)
				if not page == url:
					control.addDir("[COLOR yellow]PAGE:[/COLOR] " + page_title,page,'docstorm_cat',control.fanart,control.fanart)
        except:
			pass
			
        try:
			n = query.findAll('link', attrs = {'rel': 'prev'})
			for p in n:
				page = p['href'].encode('utf-8')
				page_title = page.split('/')[-1]
				if page_title == '': page_title = '1'
				page = urlparse.urljoin(self.base_link, page)
				if not page == url:
					control.addDir("[COLOR yellow]PAGE:[/COLOR] " + page_title,page,'docstorm_cat',control.fanart,control.fanart)
        except:
			pass

    def resolve(self, url, title, iconimage, meta):
        r = client.request(url)
        r = BeautifulSoup(r)
        r = r.findAll('iframe')
        for src in r:
			url = src['src'].encode('utf-8')
			try:host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
			except: host = 'Unknown'
			if "snagfilm" in url.lower():
				s = client.request(url)
				s = re.findall('src:\s*"(.+?)"', s)[0]
				url = s.encode('utf-8')
				
				if ".mp4?" in url: 
					url = url.split('.mp4?')[0]
					url = url + ".mp4"
				url = url + "|directplay"
				print ("SNAGFILM URL", url)
			control.addLink(host,url,'play', iconimage, control.fanart, meta)	


			
#-------------------------- GLOBAL --------------------------------------------

    def search(self, title):
        sources = []

        query = self.search_link % title
        query = urlparse.urljoin(self.base_link, query)
        r = client.request(query)
        query = BeautifulSoup(r)
        r = query.findAll('div', attrs = {'class': 'item'})
        for items in r:
			href = items.findAll('a')[0]['href'].encode('utf-8')
			img = items.findAll('img')[0]['src'].encode('utf-8')
			title = items.findAll('img')[0]['alt'].encode('utf-8')
			title = cleantitle.get2(title)
			href = urlparse.urljoin(self.base_link, href)
			img = urlparse.urljoin(self.base_link, img)
			meta = {"poster": img , "title" : title}
			meta = urllib.quote_plus(json.dumps(meta))

			sources.append({'title': title, 'provider': self.name, 'url': href, 'poster': img, 'meta':meta, 'action':'docstorm_resolve'})
        return sources		
			
