import json
import re
import urllib2
import urlparse

from BeautifulSoup import BeautifulSoup
from nanscrapers.common import random_agent, replaceHTMLCodes
from nanscrapers.scraper import Scraper


class Sezonluldizi(Scraper):
    domains = ['sezonlukdizi.com']
    name = "sezonlukdizi"

    def __init__(self):
        self.base_link = 'http://sezonlukdizi.com'

    def scrape_episode(self, title, year, season, episode, imdb, tvdb):
        url_title = title.lower().replace(' ', '-').replace('.', '-')
        episode_url = '/%s/%01d-sezon-%01d-bolum.html' % (url_title, int(season), int(episode))
        return self.sources(replaceHTMLCodes(episode_url))

    def sources(self, url):
        sources = []
        try:
            if url == None: return sources

            absolute_url = urlparse.urljoin(self.base_link, url)
            headers = {'User-Agent': random_agent()}

            request = urllib2.Request(absolute_url, headers=headers)
            html = BeautifulSoup(urllib2.urlopen(request, timeout=30).read())

            pages = []

            embed = html.findAll('div', attrs={'id': 'embed'})[0]
            pages.append(embed.findAll('iframe')[0]["src"])

            for page in pages:
                try:
                    if not page.startswith('http'):
                        page = 'http:%s' % page

                    request = urllib2.Request(page, headers=headers)
                    html = BeautifulSoup(urllib2.urlopen(request, timeout=30).read())

                    captions = html.findAll(text=re.compile('kind\s*:\s*(?:\'|\")captions(?:\'|\")'))
                    if not captions: break

                    try:
                        link_text = html.findAll(text=re.compile('url\s*:\s*\'(http(?:s|)://api.pcloud.com/.+?)\''))[0]
                        link = re.findall('url\s*:\s*\'(http(?:s|)://api.pcloud.com/.+?)\'', link_text)[0]
                        request = urllib2.Request(page, headers=headers)
                        variants = json.loads(urllib2.urlopen(request, timeout=30).read())['variants']
                        for variant in variants:
                            if 'hosts' in variant and 'path' in variant and 'height' in variant:
                                video_url = '%s%s' % (variant['hosts'][0], variant['path'])
                                heigth = variant['height']
                                if not video_url.startswith('http'):
                                    video_url = 'http://%s' % video_url
                                sources.append(
                                    {'source': 'cdn', 'quality': str(heigth), 'scraper': self.name, 'url': video_url,
                                     'direct': False})
                    except:
                        pass

                    try:
                        links_text = html.findAll(
                            text=re.compile('"?file"?\s*:\s*"([^"]+)"\s*,\s*"?label"?\s*:\s*"(\d+)p?[^"]*"'))
                        if len(links_text) > 0:
                            for link_text in links_text:
                                try:
                                    link = re.findall('"?file"?\s*:\s*"([^"]+)"\s*,\s*"?label"?\s*:\s*"(\d+)p?[^"]*"',
                                                      link_text)[0]
                                except:
                                    continue
                                video_url = link[0]
                                if not video_url.startswith('http'):
                                    video_url = 'http:%s' % video_url
                                quality = link[1]
                                sources.append(
                                    {'source': 'google video', 'quality': quality, 'scraper': self.name,
                                     'url': video_url, 'direct': True})
                    except:
                        pass
                except:
                    pass

        except:
            pass

        return sources
