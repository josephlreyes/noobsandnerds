import re
import requests
from nanscrapers.scraper import Scraper
import xbmc


class Animetoon(Scraper):
    name = "animetoon"
    domains = ['animetoon.org']
    sources = []

    def __init__(self):
        self.base_link = 'http://www.animetoon.org/'

    def scrape_episode(self, title, show_year, year, season, episode, imdb, tvdb):
        try:
            if int(season) == 1:
                url = self.base_link + title.replace(' ', '-') + '-episode-' + episode
            else:
                url = self.base_link + title.replace(' ','-')+'-season-'+season+'-episode-'+episode
            html=requests.get(url).text
            match = re.compile('"playlist">.+?</span></div><div><iframe src="(.+?)"').findall(html)
            for url2 in match:
                if 'panda' in url2:
                    HTML = requests.get(url2).text
                    match2 = re.compile("url: '(.+?)'").findall(HTML)
                    for url3 in match2:
                        if 'http' in url3:
                            self.sources.append({'source': 'playpanda', 'quality': 'SD', 'scraper': self.name, 'url': url3, 'direct': True})
                elif 'easy' in url2:
                    HTML2 = requests.get(url2).text
                    match3 = re.compile("url: '(.+?)'").findall(HTML2)
                    for url3 in match3:
                        if 'http' in url3:
                            self.sources.append({'source': 'easyvideo', 'quality': 'SD', 'scraper': self.name, 'url': url3, 'direct': True})
                elif 'zoo' in url2:
                    HTML3 = requests.get(url2).text
                    match4 = re.compile("url: '(.+?)'").findall(HTML3)
                    for url3 in match4:
                        if 'http' in url3:
                            self.sources.append({'source': 'videozoo', 'quality': 'SD', 'scraper': self.name, 'url': url3, 'direct': False})
                
                    
            return self.sources
        except:
            pass
            return []