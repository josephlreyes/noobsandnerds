# -*- coding: utf-8 -*-

'''
    Bob Add-on
    Copyright (C) 2016 Bob

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import random

import nanscrapers
import requests
import urllib
import urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import control
from resources.lib.modules import client

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database


class sources:
    @staticmethod
    def getSources(title, year, imdb, tvdb, season, episode, tvshowtitle, premiered, timeout=30,
                   progress=True, preset="search", dialog = None):

        year = str(year)

        content = 'movie' if tvshowtitle == None else 'episode'

        if content == 'movie':
            title = cleantitle.normalize(title)
            links_scraper = nanscrapers.scrape_movie(title, year, imdb, timeout=timeout)
        elif content == 'episode':
            tvshowtitle = cleantitle.normalize(tvshowtitle)
            links_scraper = nanscrapers.scrape_episode(tvshowtitle, premiered, season, episode, imdb, tvdb,
                                                       timeout=timeout)
        else:
            return

        sd_links = []
        non_direct = []
        for scraper_links in links_scraper():
            if scraper_links is not None:
                random.shuffle(scraper_links)
                for scraper_link in scraper_links:
                    if dialog is not None and dialog.iscanceled():
                        return

                    if (not control.setting('allow_openload') == 'true' and 'openload' in scraper_link['url']) or (
                                not control.setting('allow_the_video_me') == 'true' and 'thevideo.me' in scraper_link[
                                'url']):
                        continue
                    if preset.lower() == 'searchsd':
                        try:
                            quality = int(scraper_link['quality'])
                            if quality > 576:
                                continue
                        except:
                            if scraper_link['quality'] not in ["SD", "CAM", "SCR"]:
                                continue
                    elif preset.lower() == 'search':
                        try:
                            quality = int(scraper_link['quality'])
                            if quality <= 576:
                                sd_links.append(scraper_link)
                                continue
                        except:
                            if scraper_link['quality'] in ["SD", "CAM", "SCR"]:
                                sd_links.append(scraper_link)
                                continue

                    if "m4u" in scraper_link['url']:
                        if sources().check_playable(scraper_link['url']) is not None:
                            return scraper_link['url']

                    else:
                        try:
                            import urlresolver
                            resolved_url = urlresolver.resolve(scraper_link['url'])
                            if resolved_url and sources().check_playable(resolved_url) is not None:
                                url = resolved_url
                                return url
                            else:
                                continue
                        except:
                            if scraper_link['direct']:
                                url = scraper_link['url']
                                if sources().check_playable(url) is not None:
                                    return url
                            else:
                                non_direct.append(scraper_link)

        for link in sd_links:

            if dialog is not None and dialog.iscanceled():
                return

            if "m4u" in scraper_link['url']:
                return scraper_link['url']

            else:
                try:
                    import urlresolver
                    resolved_url = urlresolver.resolve(scraper_link['url'])
                    if resolved_url and sources().check_playable(resolved_url) is not None:
                       return resolved_url
                    else:
                        continue
                except:
                    if sources().check_playable(link['url']) is not None:
                        return link['url']

        try:
            import urlresolver
        except:
            control.dialog.ok("Dependency missing",
                              "please install script.mrknow.urlresolver to resolve non-direct links")
            return

        for link in non_direct:
            if dialog is not None and dialog.iscanceled():
                return

            try:
                resolved_url = urlresolver.resolve(link['url'])
            except:
                continue
            if resolved_url and sources().check_playable(resolved_url) is not None:
                url = resolved_url
                return url

    @staticmethod
    def direct_resolve(url):
        try:
            import urlresolver
        except:
            control.dialog.ok("Dependency missing",
                              "please install script.mrknow.urlresolver to resolve non-direct links")
        try:
            resolved_url = urlresolver.resolve(url)
            if resolved_url and sources().check_playable(resolved_url) is not None:
                return resolved_url
        except:
            return False


    @staticmethod
    def check_playable(url):
        try:
            headers = url.rsplit('|', 1)[1]
        except:
            headers = ''
        headers = urllib.quote_plus(headers).replace('%3D', '=') if ' ' in headers else headers
        headers = dict(urlparse.parse_qsl(headers))

        result = None

        if url.startswith('http') and '.m3u8' in url:
            result = client.request(url.split('|')[0], headers=headers, output='geturl', timeout='10')
            if result == None: return None

        elif url.startswith('http'):
            result = client.request(url.split('|')[0], headers=headers, output='chunk', timeout='10')
            if result == None: return None

        return result
