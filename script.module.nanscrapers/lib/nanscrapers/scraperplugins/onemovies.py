import base64
import hashlib
import random
import re
import string
import urllib
import urlparse

import requests
from BeautifulSoup import BeautifulSoup
from nanscrapers.common import clean_title, random_agent, replaceHTMLCodes
from nanscrapers.scraper import Scraper


class Onemovies(Scraper):
    domains = ['123movies.gs']
    name = "onemovies"

    def __init__(self):
        self.base_link = 'http://123movies.gs'
        self.search_link = '/movie/search/%s'
        self.info_link = '/ajax/movie_load_info/%s'
        self.server_link = '/ajax/get_episodes/%s'
        self.direct_link = '/ajax/v2_load_episode/'
        self.embed_link = '/ajax/load_embed/'

    def scrape_movie(self, title, year, imdb):
        try:
            # print("ONEMOVIES")
            headers = {'User-Agent': random_agent()}
            # print("ONEMOVIES", headers)
            query = self.search_link % (urllib.quote_plus(title.replace("'", " ")))
            query = urlparse.urljoin(self.base_link, query)
            cleaned_title = clean_title(title)
            # print("ONEMOVIES", query)
            html = BeautifulSoup(requests.get(query, headers=headers, timeout=30).content)
            containers = html.findAll('div', attrs={'class': 'ml-item'})
            for result in containers:
                links = result.findAll('a')
                # print("ONEMOVIES", links)
                for link in links:
                    link_title = str(link['title'])
                    href = str(link['href'])
                    info = str(link['data-url'])
                    # print("ONEMOVIES", link_title, href, info)
                    if clean_title(link_title) == cleaned_title:
                        html = requests.get(info, headers=headers).content
                        pattern = '<div class="jt-info">%s</div>' % year
                        match = re.findall(pattern, html)
                        if match:
                            # print("ONEMOVIES MATCH", href)
                            return self.sources(replaceHTMLCodes(href))



        except:
            pass
        return []

    def scrape_episode(self, title, show_year, year, season, episode, imdb, tvdb):
        try:
            headers = {'User-Agent': random_agent()}
            query = "%s+season+%s" % (urllib.quote_plus(title), season)
            query = self.search_link % query
            query = urlparse.urljoin(self.base_link, query)
            cleaned_title = clean_title(title)
            checkseason = cleaned_title + "season" + season
            # print("ONEMOVIES", query,checkseason)
            html = BeautifulSoup(requests.get(query, headers=headers, timeout=30).content)
            containers = html.findAll('div', attrs={'class': 'ml-item'})
            for result in containers:
                links = result.findAll('a')
                # print("ONEMOVIES", links)
                for link in links:
                    link_title = str(link['title'])
                    href = str(link['href'])

                    # print("ONEMOVIES", link_title, href, info)
                    if clean_title(link_title) == checkseason:
                        ep_id = '?episode=%01d' % int(episode)
                        href = href + ep_id
                        # print("ONEMOVIES Passed", href)
                        return self.sources(replaceHTMLCodes(href))

        except:
            pass
        return []

    def sources(self, url):
        sources = []
        try:
            # print("ONEMOVIES SOURCES", url)

            if url == None: return sources
            referer = url
            headers = {'User-Agent': random_agent()}
            url = url.replace('/watching.html', '')
            html = requests.get(url, headers=headers).content
            # print ("ONEMOVIES Source", html)
            try:
                url, episode = re.findall('(.+?)\?episode=(\d*)$', url)[0]
            except:
                episode = None
            vid_id = re.findall('-(\d+)', url)[-1]
            # print ("ONEMOVIES", vid_id)
            quality = re.findall('<span class="quality">(.*?)</span>', html)
            quality = str(quality)
            if quality == 'cam' or quality == 'ts':
                quality = 'CAM'
            elif quality == 'hd':
                quality = '720'
            else:
                quality = '480'
            try:
                headers = {'X-Requested-With': 'XMLHttpRequest'}
                headers['Referer'] = referer
                headers['User-Agent'] = random_agent()
                u = urlparse.urljoin(self.base_link, self.server_link % vid_id)
                # print("SERVERS", u)
                r = BeautifulSoup(requests.get(u, headers=headers).content)
                # print("SERVERS", r)
                containers = r.findAll('div', attrs={'class': 'les-content'})
                for result in containers:
                    links = result.findAll('a')
                    # print("ONEMOVIES", links)
                    for link in links:
                        title = str(link['title'])
                        # print("ONEMOVIES TITLE", title)
                        if not episode == None:
                            title = re.findall('Episode\s+(\d+):', title)[0]
                            title = '%01d' % int(title)
                            if title == episode:
                                episode_id = str(link['episode-id'])
                            # print("ONEMOVIES EPISODE", episode_id)
                            else:
                                continue

                        else:
                            episode_id = str(link['episode-id'])
                        onclick = str(link['onclick'])

                        key_gen = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(16))
                        ################# FIX FROM MUCKY DUCK & XUNITY TALK ################
                        key = '87wwxtp3dqii'
                        key2 = '7bcq9826avrbi6m49vd7shxkn985mhod'
                        cookie = hashlib.md5(episode_id + key).hexdigest() + '=%s' % key_gen
                        a = episode_id + key2
                        b = key_gen
                        i = b[-1]
                        h = b[:-1]
                        b = i + h + i + h + i + h
                        hash_id = uncensored(a, b)
                        ################# FIX FROM MUCKY DUCK & XUNITY TALK ################

                        serverurl = self.base_link + '/ajax/v2_get_sources/' + episode_id + '?hash=' + urllib.quote(
                            hash_id)
                        # print ("playurl ONEMOVIES", serverurl)

                        headers = {'Accept-Language': 'en-US', 'Cookie': cookie, 'Referer': referer,
                                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36',
                                   'X-Requested-With': 'XMLHttpRequest'}
                        # print ("playurl ONEMOVIES", headers)
                        result = requests.get(serverurl, headers=headers).content
                        # print ("RESULT ONEMOVIES", result)
                        result = result.replace('\\', '')
                        # print ("ONEMOVIES Result", result)
                        url = re.findall('"?file"?\s*:\s*"(.+?)"', result)
                        url = [googletag(i) for i in url]
                        url = [i[0] for i in url if len(i) > 0]
                        u = []
                        try:
                            u += [[i for i in url if i['quality'] == '1080p'][0]]
                        except:
                            pass
                        try:
                            u += [[i for i in url if i['quality'] == '720'][0]]
                        except:
                            pass
                        try:
                            u += [[i for i in url if i['quality'] == '480'][0]]
                        except:
                            pass
                        url = replaceHTMLCodes(u[0]['url'])
                        quality = googletag(url)[0]['quality']

                        # print ("ONEMOVIES PLAY URL", quality, url)

                        sources.append({'source': 'google video', 'quality': quality, 'scraper': self.name, 'url': url,
                                        'direct': True})
            except:
                pass

        except:
            pass
        return sources


def uncensored(a, b):
    n = -1
    fuckme = []
    justshow = []
    while True:

        if n == len(a) - 1:
            break
        n += 1

        d = int(''.join(str(ord(c)) for c in a[n]))

        e = int(''.join(str(ord(c)) for c in b[n]))
        justshow.append(d + e)
        fuckme.append(chr(d + e))

    return base64.b64encode(''.join(fuckme))


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
