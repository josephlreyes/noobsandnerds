import re
import urllib2
import urlparse

from BeautifulSoup import BeautifulSoup
from nanscrapers.common import clean_title, random_agent, replaceHTMLCodes, odnoklassniki, vk
from nanscrapers.scraper import Scraper


class Dizigold(Scraper):
    domains = ['dizigold.net']
    name = "dizigold"

    def __init__(self):
        self.base_link = 'http://www.dizigold.net'
        self.player_link = 'http://player.dizigold.net/?id=%s&s=1&dil=or'

    def scrape_episode(self, title, year, season, episode, imdb, tvdb):

        url_title = clean_title(title).replace(' ', '-').replace('.', '-')
        episode_url = '/%s/%01d-sezon/%01d-bolum' % (url_title, int(season), int(episode))
        return self.sources(replaceHTMLCodes(episode_url))

    def sources(self, url):
        sources = []
        try:
            if url == None: return sources

            referer = urlparse.urljoin(self.base_link, url)

            headers = {}
            headers['Referer'] = referer
            headers['User-Agent'] = random_agent()

            request = urllib2.Request(referer, headers=headers)
            html = urllib2.urlopen(request, timeout=30).read()

            player_id = re.compile('var\s*view_id\s*=\s*"(\d*)"').findall(html)[0]
            player_url = self.player_link % player_id
            player_request = urllib2.Request(player_url, headers=headers)
            player_html = urllib2.urlopen(player_request, timeout=30).read()
            player_html_parsed = BeautifulSoup(player_html)

            try:
                video_url = player_html_parsed.findAll('iframe')[-1]['src']

                if 'openload' in video_url:
                    host = 'openload.co'
                    direct = False
                    video_url = [{'url': video_url, 'quality': 'HD'}]

                elif 'ok.ru' in video_url:
                    host = 'vk'
                    direct = True
                    video_url = odnoklassniki(video_url)

                elif 'vk.com' in video_url:
                    host = 'vk'
                    direct = True
                    video_url = vk(video_url)

                else:
                    raise Exception()

                for i in video_url: sources.append(
                    {'source': host, 'quality': i['quality'], 'scraper': self.name, 'url': i['url'], 'direct': direct})
            except:
                pass

            try:

                links = re.compile('"?file"?\s*:\s*"([^"]+)"\s*,\s*"?label"?\s*:\s*"(\d+)p?"').findall(player_html)

                for link in links: sources.append(
                    {'source': 'google video', 'quality': link[1], 'scraper': self.name, 'url': link[0], 'direct': True})

            except:
                pass

        except:
            pass

        return sources
