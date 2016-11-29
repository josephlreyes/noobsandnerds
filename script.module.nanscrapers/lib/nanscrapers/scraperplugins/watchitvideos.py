import re
import requests
from nanscrapers.scraper import Scraper

class Watchitvideos(Scraper):
    domains = ['watchitvideos']
    name = "watchitvideos"
    sources = []

    def __init__(self):
        self.base_link = 'http://watchitvideos.me/'

    def scrape_movie(self, title, year, imdb):
        try:
            url_list=[self.base_link+title.replace(' ','-')+'-'+year+'-free-online-putlocker2/',
                      self.base_link+title.replace(' ','-')+'-'+year+'-putlocker2/']
            for start_url in url_list:
                print start_url
                html = requests.get(start_url).text
                url = re.compile('&quot;http(.+?)&quot').findall(html)
                for link in url:
                    source_link = 'http'+link
                    if 'thevideo.me' in source_link:
                        pass
                    elif 'streamin.to' in source_link:
                        self.sources.append({'source': 'streamin.to', 'quality': 'SD', 'scraper': self.name, 'url': source_link,'direct': False})
                    elif 'uptostream.com' in source_link:
                        self.sources.append({'source': 'uptostream.com', 'quality': 'SD', 'scraper': self.name, 'url': source_link,'direct': False})
                    elif 'vidbull.com' in source_link:
                        self.sources.append({'source': 'vidbull.com', 'quality': 'SD', 'scraper': self.name, 'url': source_link,'direct': False})
                    elif 'thevideos.tv' in source_link:
                        html2 = requests.get(source_link).text
                        get_link = re.compile('file:"(.+?)",label:"(.+?)"').findall(html2)
                        for url,p in get_link:
                            stream_source = 'thevideos.tv'
                            quality = p
                            playlink = url
                            self.sources.append({'source': stream_source, 'quality': quality, 'scraper': self.name, 'url': playlink,'direct': True})

        except:
            pass

        return self.sources


