import json
import re
import urllib
import urllib2
import urlparse

from BeautifulSoup import BeautifulSoup
from nanscrapers import proxy
from nanscrapers.common import clean_title, random_agent, replaceHTMLCodes
from nanscrapers.scraper import Scraper


class Xmovies(Scraper):
    domains = ['xmovies8.ru']
    name = "xmovies"

    def __init__(self):
        self.base_link = 'http://xmovies8.ru'
        self.search_link = '/movies/search?s=%s'

    def scrape_movie(self, title, year, imdb):
        try:
            headers = {'User-Agent': random_agent()}
            query = urlparse.urljoin(self.base_link, self.search_link)
            query = query % urllib.quote_plus(title)
            # print ("XMOVIES query", query)
            cleaned_title = clean_title(title)
            request = urllib2.Request(query, headers=headers)
            html = BeautifulSoup(urllib2.urlopen(request, timeout=30))
            containers = html.findAll('div', attrs={'class': 'item_movie'})
            # print ("XMOVIES r1", containers)
            for container in containers:
                try:
                    links = container.findAll('h2', attrs={'class': 'tit'})[0]
                    r = links.findAll('a')
                    for link in r:
                        link_title = link['title'].encode('utf-8')
                        href = link['href'].encode('utf-8')
                        if len(link_title) > 0 and len(href) > 0:
                            parsed = re.findall('(.+?) \((\d{4})', link_title)
                            parsed_title = parsed[0][0]
                            parsed_years = parsed[0][1]
                            if cleaned_title.lower() == clean_title(parsed_title).lower() and year == parsed_years:
                                if not "http:" in href: href = "http:" + href
                                return self.sources(replaceHTMLCodes(href))
                except:
                    pass
        except:
            pass
        return []

    def sources(self, url):
        sources = []
        try:
            if url == None: return sources

            absolute_url = urlparse.urljoin(self.base_link, url)
            referer_url = url.replace('watching.html', '') + 'watching.html'

            headers = {'User-Agent': random_agent}
            request = urllib2.Request(absolute_url, headers=headers)
            post = urllib2.urlopen(request, timeout=30).read()

            post = re.findall('movie=(\d+)', post)[0]
            post = urllib.urlencode({'id': post, 'episode_id': '0', 'link_id': '0', 'from': 'v3'})

            headers = {'X-Requested-With': 'XMLHttpRequest', 'Accept-Formating': 'application/json, text/javascript',
                       'Server': 'cloudflare-nginx'}
            headers['Referer'] = referer_url
            headers['User-Agent'] = random_agent()
            load_episode_url = urlparse.urljoin(self.base_link, '/ajax/movie/load_episodes')
            request = urllib2.Request(load_episode_url, data=post, headers=headers)

            html = BeautifulSoup(urllib2.urlopen(request))

            pattern = re.compile("load_player\(\s*'([^']+)'\s*,\s*'?(\d+)\s*'?")
            links = html.findAll('a', attrs={'onclick': pattern})

            for link in links:
                info = re.findall(pattern, link['onclick'])[0]  # (id, quality) quality can be 0
                try:
                    play = urlparse.urljoin(self.base_link, '/ajax/movie/load_player_v2')
                    post = urllib.urlencode({'id': info[0], 'quality': info[1]})
                    request_play = urllib2.Request(play, data=post, headers=headers)
                    player_url = urllib2.urlopen(request_play).read()

                    json_url = json.loads(player_url)['link']

                    response = proxy.get_raw(json_url, headers=headers)
                    video_url = response.geturl()

                    try:
                        unproxied_video_url = urlparse.parse_qs(urlparse.urlparse(video_url).query)['u'][0]
                    except:
                        pass
                    try:
                        unproxied_video_url = urlparse.parse_qs(urlparse.urlparse(video_url).query)['q'][0]
                    except:
                        pass
                        pass

                    if 'openload.' in unproxied_video_url:
                        sources.append(
                            {'source': 'openload.co', 'quality': 'HD', 'scraper': self.name, 'url': unproxied_video_url,
                             'direct': False})

                    else:
                        sources.append(
                            {'source': 'google video', 'quality': googletag(unproxied_video_url )[0]['quality'],
                             'scraper': self.name, 'url': unproxied_video_url, 'direct': True})
                except:
                    continue
            return sources
        except:
            return sources


def googletag(url):
    quality = re.compile('itag=(\d*)').findall(url)
    quality += re.compile('=m(\d*)$').findall(url)
    try:
        quality = quality[0]
    except:
        return []

    if quality in ['37', '137', '299', '96', '248', '303', '46']:
        return [{'quality': '1080', 'url': url}]
    elif quality in ['22', '84', '136', '298', '120', '95', '247', '302', '45', '102']:
        return [{'quality': '720', 'url': url}]
    elif quality in ['35', '44', '135', '244', '94']:
        return [{'quality': '480', 'url': url}]
    elif quality in ['18', '34', '43', '82', '100', '101', '134', '243', '93']:
        return [{'quality': '480', 'url': url}]
    elif quality in ['5', '6', '36', '83', '133', '242', '92', '132']:
        return [{'quality': '480', 'url': url}]
    else:
        return []
