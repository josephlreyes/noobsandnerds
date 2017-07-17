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
		
        self.name = 'TopDocs'

        self.base_link = 'http://topdocumentaryfilms.com'
        self.search_link = '/search/%s/feed/rss2/'

    def get(self):
        control.addDir('Top 100',self.base_link + '/top-100/','topdocs_popular',control.fanart,control.fanart)
        r = client.request(self.base_link)
        r = BeautifulSoup(r)
        r = r.findAll('ul', attrs = {'class': 'cat-list'})
        for items in r:
			u = items.findAll('a')
			for s in u:
				url = s['href'].encode('utf-8')
				title = s.string
				url = urlparse.urljoin(self.base_link, url)
				control.addDir(title,url,'topdocs_cat',control.fanart,control.fanart)

    def popular(self, url):
        r = client.request(url)
        r = client.parseDOM(r, 'span', attrs = {'itemprop': 'itemListElement'})
        for items in r:
                try:
					href = client.parseDOM(items, 'a', ret='href')[0].encode('utf-8')
					title = client.parseDOM(items, 'a', ret='title')[0].encode('utf-8')
					img = client.parseDOM(items, 'img', ret='src')[0].encode('utf-8')
					href = urlparse.urljoin(self.base_link, href)
					img = urlparse.urljoin(self.base_link, img)
					meta = {"poster": img , "title" : title}
					meta = urllib.quote_plus(json.dumps(meta))
					control.addDirMeta(title,href,'topdocs_resolve', img, control.fanart, meta)
                except:
					pass

			

    def cat(self, url):
	
        try:

			r = client.request(url)
			query = BeautifulSoup(r)
			r = query.findAll('span', attrs = {'class': 'excerptpic'})
			for items in r:
				
				href = items.findAll('a')[0]['href'].encode('utf-8')
				img = items.findAll('img')[0]['src'].encode('utf-8')
				title = items.findAll('a')[0]['title'].encode('utf-8')
				title = cleantitle.get2(title)
				href = urlparse.urljoin(self.base_link, href)
				img = urlparse.urljoin(self.base_link, img)
				meta = {"poster": img , "title" : title}
				meta = urllib.quote_plus(json.dumps(meta))
				control.addDirMeta(title,href,'topdocs_resolve', img, control.fanart, meta)
				
        except:
			pass
			
        try:
			n = query.findAll('div', attrs = {'class': 'pagination module'})
			for x in n:
				pages = x.findAll('a')
				for p in pages:
					page = p['href'].encode('utf-8')
					page = urlparse.urljoin(self.base_link, page)
					page_title = p.string
					if not page == url:
						control.addDir("[COLOR yellow]PAGE:[/COLOR] " + page_title,page,'topdocs_cat',control.fanart,control.fanart)
        except:
			pass


    def resolve(self, url, title, iconimage, meta):
        r = client.request(url)
        r = BeautifulSoup(r)
        r = r.findAll('iframe')
        for src in r:
			url = src['src'].encode('utf-8')
			if url.startswith('/'): url = "https:" + url
			try:host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
			except: host = 'Unknown'
			control.addLink(host,url,'play', iconimage, control.fanart, meta)	


			
#-------------------------- GLOBAL --------------------------------------------

    def search(self, title):
        sources = []

        query = self.search_link % title
        query = urlparse.urljoin(self.base_link, query)
        r = client.request(query)
        posts = client.parseDOM(r, 'item')

 
        for items in posts:
								
			url = client.parseDOM(items, 'link')[0].encode('utf-8')
			title = client.parseDOM(items, 'title')[0].encode('utf-8')

			
			img = client.parseDOM(items, 'img', ret='src')[0].encode('utf-8')
			print ("DOCHEAVEN SEARCH", url,title,img)

			title = cleantitle.get2(title)
			url = urlparse.urljoin(self.base_link, url)
			img = urlparse.urljoin(self.base_link, img)
			meta = {"poster": img , "title" : title}
			meta = urllib.quote_plus(json.dumps(meta))

			sources.append({'title': title, 'provider': self.name, 'url': url, 'poster': img, 'meta':meta, 'action':'topdocs_resolve'})
        return sources		
			
