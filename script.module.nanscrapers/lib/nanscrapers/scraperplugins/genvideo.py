import re
import urllib
import urllib2
import urlparse

from BeautifulSoup import BeautifulSoup
from nanscrapers.common import clean_title, random_agent, replaceHTMLCodes
from nanscrapers.scraper import Scraper


class Genvideo(Scraper):
    domains = ['genvideos.org']
    name = "genvideo"

    def __init__(self):
        self.base_link = 'http://genvideos.org'
        self.search_link = '/results?q=%s'

    def scrape_movie(self, title, year, imdb):
        try:
            headers = {'User-Agent': random_agent()}
            query = self.search_link % (urllib.quote_plus(title))
            query = urlparse.urljoin(self.base_link, query)
            cleaned_title = clean_title(title)
            request = urllib2.Request(query, headers=headers)
            html = BeautifulSoup(urllib2.urlopen(request, timeout=30))
            containers = html.findAll('div', attrs={'class': 'cell_container'})
            for container in containers:
                links = container.findAll('a')
                for link in links:
                    link_title = link['title']
                    href = link['href']
                    if len(link_title) > 0 and len(href) > 0:
                        parsed = re.findall('(.+?) \((\d{4})', link_title)
                        parsed_title = parsed[0][0]
                        parsed_years = parsed[0][1]
                        if cleaned_title == clean_title(parsed_title) and year == parsed_years:
                            return self.sources(replaceHTMLCodes(href))
        except:
            pass
        return []

    def sources(self, url):
        sources = []
        try:
            if url == None: return sources

            referer = urlparse.urljoin(self.base_link, url)

            headers = {'X-Requested-With': 'XMLHttpRequest'}
            headers['Referer'] = referer
            headers['User-Agent'] = random_agent()

            post = urlparse.parse_qs(urlparse.urlparse(referer).query).values()[0][0]
            post = urllib.urlencode({'v': post})

            url = urlparse.urljoin(self.base_link, '/video_info/iframe')

            request = urllib2.Request(url, data=post, headers=headers)
            html = urllib2.urlopen(request).read()

            quality_url_pairs = re.findall('"(\d+)"\s*:\s*"([^"]+)', html)

            for pair in quality_url_pairs:
                quality = pair[0]
                url = urllib.unquote(pair[1].split('url=')[-1])
                sources.append(
                    {'source': 'google video', 'quality': quality, 'scraper': self.name, 'url': url, 'direct': True})
        except:
            pass

        return sources
