import re
import urllib
import urllib2
import urlparse
import xbmc

from BeautifulSoup import BeautifulSoup
from nanscrapers.common import random_agent, replaceHTMLCodes
from nanscrapers.scraper import Scraper
import StringIO
import gzip

class Pubfilm(Scraper):
    domains = ['pubfilmno1.com', 'pubfilm.com', 'pidtv.com']
    name = "pubfilm"

    def __init__(self):
        self.base_link = 'http://pubfilm.com'
        self.moviesearch_hd_link = '/%s-%s-full-hd-pubfilm-free.html'
        self.moviesearch_sd_link = '/%s-%s-pubfilm-free.html'
        self.tvsearch_link = '/wp-admin/admin-ajax.php'

    def scrape_movie(self, title, year, imdb):
        try:
            title = title.translate(None, '\/:*?"\'<>|!,').replace(' ', '-').replace('--', '-').lower()
            headers = {'User-Agent': random_agent()}
            search_url = urlparse.urljoin(self.base_link, self.moviesearch_hd_link % (title, year))
            html = None
            try:
                request = urllib2.Request(search_url, headers=headers)
                html = BeautifulSoup(urllib2.urlopen(request, timeout=30))
            except:
                pass

            if html == None:
                search_url = urlparse.urljoin(self.base_link, self.moviesearch_sd_link % (title, year))

                request = urllib2.Request(search_url, headers=headers)
                html = BeautifulSoup(urllib2.urlopen(request, timeout=30))

            if html == None:
                raise Exception()

            #url = re.findall('(?://.+?|)(/.+)', search_url)[0]
            return self.sources(search_url)
        except:
            pass
        return []

    def scrape_episode(self, title, year, season, episode, imdb, tvdb):
        try:
            for try_year in [str(year), str(int(year) - 1)]:
                tvshowtitle = '%s %s: Season %s' % (title, try_year, season)
                headers = {'X-Requested-With': 'XMLHttpRequest',
                           'User-Agent': random_agent()}

                post = urllib.urlencode({'aspp': tvshowtitle, 'action': 'ajaxsearchpro_search',
                                         'options': 'qtranslate_lang=0&set_exactonly=checked&set_intitle=None&customset[]=post',
                                         'asid': '4', 'asp_inst_id': '4_1'})

                url = urlparse.urljoin(self.base_link, self.tvsearch_link)
                request = urllib2.Request(url, data= post, headers=headers)
                html = BeautifulSoup(urllib2.urlopen(request, timeout=30))
                links = html.findAll('a', attrs={'class': 'asp_res_url'})
                show_url = None
                for link in links:
                    href = link["href"]
                    link_tvshowtitle = re.findall('(.+?: Season \d+)', link.contents[0].strip())[0]
                    if title.lower() in link_tvshowtitle.lower() and str(season) in link_tvshowtitle:
                        if try_year in link_tvshowtitle:
                            show_url = href
                            break
                if show_url is None:
                    continue
                episode_url = show_url + '?episode=%01d' % int(episode)
                return self.sources(episode_url)
        except:
            pass
        return []


    def sources(self, url):
        sources = []
        try:
            if url == None: return sources

            if not self.base_link in url:
                url = urlparse.urljoin(self.base_link, url)

            content = re.compile('(.+?)\?episode=\d*$').findall(url)
            video_type = 'movie' if len(content) == 0 else 'episode'

            try:
                url, episode = re.compile('(.+?)\?episode=(\d*)$').findall(url)[0]
            except:
                pass

            headers = {'User-Agent': random_agent()}
            request = urllib2.Request(url, headers=headers)

            html = urllib2.urlopen(request).read()

            try:
                compressedstream = StringIO.StringIO(html)
                html = gzip.GzipFile(fileobj=compressedstream).read()
                html = BeautifulSoup(html)
            except:
                html = BeautifulSoup(html)

            links = html.findAll('a', attrs={'target': 'EZWebPlayer'})
            for link in links:
                href = replaceHTMLCodes(link['href'])

                if video_type == 'episode':
                    link_episode_number = re.compile('(\d+)').findall(link.string)
                    if len(link_episode_number) > 0:
                        link_episode_number = link_episode_number[-1]
                        if not link_episode_number == '%01d' % int(episode):
                            continue

                referer = url
                headers = {'User-Agent': random_agent(), 'Referer': referer}
                request = urllib2.Request(href, headers=headers)
                html = urllib2.urlopen(request).read()

                source = re.findall('movie_sources\s*:\s*\[(.+?)\]', html)[0]
                files = re.findall('"file"\s*:\s*"(.+?)".+?"label"\s*:\s*"(.+?)"', source)

                quality_url_pairs = [{'url': file[0], 'quality': file[1][:-1]} for file in files]

                for pair in quality_url_pairs:
                    sources.append(
                        {'source': 'google video', 'quality': pair['quality'], 'scraper': self.name, 'url': pair['url'],
                         'direct': True})
        except:
            pass

        return sources
