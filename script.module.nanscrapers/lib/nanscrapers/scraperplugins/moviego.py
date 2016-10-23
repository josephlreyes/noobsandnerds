import json
import re
import urllib
import urllib2
import urlparse

from BeautifulSoup import BeautifulSoup
from nanscrapers.common import clean_title, random_agent, replaceHTMLCodes
from nanscrapers.scraper import Scraper


class Moviego(Scraper):
    domains = ['moviego.cc']
    name = "moviego"

    def __init__(self):
        self.base_link = 'http://moviego.cc'
        self.search_link = '/index.php?do=search&subaction=search&full_search=1&result_from=1&story=%s+%s'
        self.ep_url = '/engine/ajax/getlink.php?id=%s'

    def scrape_movie(self, title, year, imdb):
        try:
            # print("MOVIEGO INIT")
            headers = {'User-Agent': random_agent()}
            searchquery = self.search_link % (urllib.quote_plus(title), year)
            query = urlparse.urljoin(self.base_link, searchquery)
            cleaned_title = clean_title(title)
            request = urllib2.Request(query, headers=headers)
            html = urllib2.urlopen(request, timeout=30).read()
            html = BeautifulSoup(html)

            containers = html.findAll('div', attrs={'class': 'short_content'})
            # print("MOVIEGO MOVIES",containers)
            for items in containers:
                href = items.findAll('a')[0]['href']
                title = items.findAll('div', attrs={'class': 'short_header'})[0]
                if year in str(title):
                    title = normalize(str(title))
                    if title == cleaned_title:
                        # print("MOVIEGO MOVIES PASSED", href)
                        return self.sources(replaceHTMLCodes(href))

        except:
            return []

    def sources(self, url):
        sources = []
        try:

            if url == None: return sources
            headers = {'User-Agent': random_agent()}
            request = urllib2.Request(url, headers=headers)
            link = urllib2.urlopen(request, timeout=30).read()
            url = re.findall('file:\s+"(.*?)",', link)[0]
            film_id = re.findall("\/(\d+)-", link)[0]
            film_quality = re.findall('<div class="poster-qulabel">(.*?)</div>', link)[0]
            # print ("MOVIEGO Sources", url,film_id,film_quality)
            if film_id:
                try:
                    film_id = film_id.encode('utf-8')
                    try:
                        film_quality = film_quality.encode('utf-8')
                    except:
                        pass
                    # print ("MOVIEGO RESULTS", film_id,film_quality)
                    ep_query = self.ep_url % film_id
                    query = urlparse.urljoin(self.base_link, ep_query)
                    # print("MOVIEGO MOVIES query",query)
                    request_query = urllib2.Request(query, headers=headers)
                    linkquery = urllib2.urlopen(request_query, timeout=30).read()
                    # print ("MOVIEGO 3r", linkquery)
                    results = json.loads(linkquery)
                    url = results['file']
                    # print ("MOVIEGO 3r", url)
                    if "1080" in film_quality:
                        quality = "1080"
                    elif "720" in film_quality:
                        quality = "720"
                    else:
                        quality = "480"
                    url = url.encode('utf-8')
                    sources.append({'source': 'google video', 'quality': quality, 'scraper': self.name, 'url': url,
                                    'direct': True})
                except:
                    pass
            if url:
                try:
                    film_quality = film_quality.encode('utf-8')
                except:
                    pass
                if "1080" in film_quality:
                    quality = "1080"
                elif "720" in film_quality:
                    quality = "720"
                else:
                    quality = "480"
                url = url.encode('utf-8')
                sources.append(
                    {'source': 'google video', 'quality': quality, 'scraper': self.name, 'url': url, 'direct': True})


        except:
            pass
        return sources


def normalize(title):
    if title == None: return
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\n|([<].+?[>])|([[].+?[]])|([(].+?[)])|\s(vs|v[.])\s|(:|;|-|"|,|\'|\_|\.|\?)|\s', '', title).lower()
    return title
