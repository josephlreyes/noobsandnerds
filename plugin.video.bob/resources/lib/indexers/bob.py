# -*- coding: utf-8 -*-

"""
    Bob Add-on

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
"""

import base64
import hashlib
import json
import os
import re
import sys
import urllib

import urlparse
import xbmc

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

from resources.lib.modules import cache
from resources.lib.modules import metacache
from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import workers
from resources.lib.modules import views


class Indexer:
    def __init__(self):
        self.list = []

    def get(self, url, result=None):
        try:
            self.list = self.bob_list(url, result)
            self.worker()
            self.add_directory(self.list, parent_url=url)
            return self.list
        except:
            pass

    def root(self):
        self.get("http://norestrictions.club/main/main.xml")

    def getx(self, url):
        self.get('', url)

    def developer(self):
        try:
            url = os.path.join(control.dataPath, 'testings.xml')
            f = control.openFile(url)
            result = f.read()
            f.close()
            self.getx(result)
        except:
            pass

    def search(self):
        try:
            self.list = [{'name': 30702, 'action': 'add_search'}]
            self.list += [{'name': 30703, 'action': 'delete_search'}]

            try:
                def search():
                    return

                query = cache.get(search, 600000000, table='rel_srch')

                for url in query:
                    try:
                        self.list += [{'name': '%s...' % url, 'url': url, 'action': 'add_search'}]
                    except:
                        pass
            except:
                pass

            self.add_directory(self.list)
            return self.list
        except:
            pass

    @staticmethod
    def delete_search():
        try:
            cache.clear('rel_srch')
            control.refresh()
        except:
            pass

    def add_search(self, url=None):
        try:
            link = 'http://norestrictions.club/main/search.xml'

            if url is None or url == '':
                keyboard = control.keyboard('', control.lang(30702).encode('utf-8'))
                keyboard.doModal()
                if not (keyboard.isConfirmed()):
                    return
                url = keyboard.getText()

            if url is None or url == '':
                return

            def search():
                return [url]

            query = cache.get(search, 600000000, table='rel_srch')

            def search():
                return [x for y, x in enumerate((query + [url])) if x not in (query + [url])[:y]]

            cache.get(search, 0, table='rel_srch')

            links = client.request(link)
            links = re.findall('<link>(.+?)</link>', links)
            links = [i for i in links if str(i).startswith('http')]

            self.list = []
            threads = []
            for link in links:
                threads.append(workers.Thread(self.bob_list, link))
            [i.start() for i in threads]
            [i.join() for i in threads]

            self.list = [i for i in self.list if url.lower() in i['name'].lower()]

            for i in self.list:
                try:
                    name = ''
                    if not i['vip'] in ['Phoenix TV']:
                        name += '[B]%s[/B] | ' % i['vip'].upper()
                    name += i['name']
                    i.update({'name': name})
                except:
                    pass

            self.add_directory(self.list, mode=False)
        except:
            pass

    @staticmethod
    def bob_get_tag_content(collection, tag, default):
        try:
            result = re.findall('<%s>(.+?)</%s>' % (tag, tag), collection)[0]
            return result
        except:
            return default

    def bob_list(self, url, result=None):
        try:
            original_url = url
            if result is None:
                result = cache.get(client.request, 0, url)

            if result.strip().startswith('#EXTM3U') and '#EXTINF' in result:
                result = re.compile('#EXTINF:.+?\,(.+?)\n(.+?)\n', re.MULTILINE | re.DOTALL).findall(result)
                result = ['<item><title>%s</title><link>%s</link></item>' % (i[0], i[1]) for i in result]
                result = ''.join(result)

            try:
                r = base64.b64decode(result)
            except:
                r = ''
            if '</link>' in r:
                result = r

            result = str(result)

            result = self.account_filter(result)

            info = result.split('<item>')[0].split('<dir>')[0]

            vip = self.bob_get_tag_content(info, 'poster', '0')
            image = self.bob_get_tag_content(info, 'thumbnail', '0')
            fanart = self.bob_get_tag_content(info, 'fanart', '0')

            items = re.compile(
                '((?:<item>.+?</item>|<dir>.+?</dir>|<plugin>.+?</plugin>|<info>.+?</info>|'
                '<name>[^<]+</name><link>[^<]+</link><thumbnail>[^<]+</thumbnail><mode>[^<]+</mode>|'
                '<name>[^<]+</name><link>[^<]+</link><thumbnail>[^<]+</thumbnail><date>[^<]+</date>))',
                re.MULTILINE | re.DOTALL).findall(result)
        except:
            return

        added_all_episodes = False
        for item in items:
            try:
                regex = re.compile('(<regex>.+?</regex>)', re.MULTILINE | re.DOTALL).findall(item)
                regex = ''.join(regex)
                regex = urllib.quote_plus(regex)

                item = item.replace('\r', '').replace('\n', '').replace('\t', '').replace('&nbsp;', '')
                item = re.sub('<link></link>|<sublink></sublink>', '', item)

                name = item.split('<meta>')[0].split('<regex>')[0]
                try:
                    name = re.findall('<title>(.+?)</title>', name)[0]
                except:
                    name = re.findall('<name>(.+?)</name>', name)[0]
                if '<meta>' in name:
                    raise Exception()

                date = self.bob_get_tag_content(item, 'date', '')
                if re.search(r'\d+', date):
                    name += ' [COLOR red] Updated %s[/COLOR]' % date
                meta = self.bob_get_tag_content(item, 'meta', '0')
                url = self.bob_get_tag_content(item, 'link', '0')

                url = url.replace('>search<', '><preset>search</preset>%s<' % meta)
                url = '<preset>search</preset>%s' % meta if url == 'search' else url
                url = url.replace('>searchsd<', '><preset>searchsd</preset>%s<' % meta)
                url = '<preset>searchsd</preset>%s' % meta if url == 'searchsd' else url
                url = url.replace('<sublink></sublink>', '')
                url += regex

                if item.startswith('<item>'):
                    action = 'play'
                elif item.startswith('<plugin>'):
                    action = 'plugin'
                elif item.startswith('<info>') or url == '0':
                    action = '0'
                else:
                    action = 'directory'

                if action in ['directory', 'plugin']:
                    folder = True
                elif not regex == '':
                    folder = True
                else:
                    folder = False

                image2 = self.bob_get_tag_content(item, 'thumbnail', image)
                if not str(image2).lower().startswith('http'):
                    image2 = '0'

                fanart2 = self.bob_get_tag_content(item, 'fanart', fanart)
                if not str(fanart2).lower().startswith('http'):
                    fanart2 = '0'

                content = self.bob_get_tag_content(meta, 'content', '0')
                if not content == '0':
                    content += 's'

                imdb = self.bob_get_tag_content(meta, 'imdb', '0')
                tvdb = self.bob_get_tag_content(meta, 'tvdb', '0')
                tvshowtitle = self.bob_get_tag_content(meta, 'tvshowtitle', '0')
                title = self.bob_get_tag_content(meta, 'title', '0')
                if title == '0' and not tvshowtitle == '0':
                    title = tvshowtitle

                year = self.bob_get_tag_content(meta, 'year', '0')
                premiered = self.bob_get_tag_content(meta, 'premiered', '0')
                season = self.bob_get_tag_content(meta, 'season', '0')
                episode = self.bob_get_tag_content(meta, 'episode', '0')

                if season is not '0' and episode is '0' and added_all_episodes is False:
                    self.list.append(
                        {'name': "All Episodes", 'vip': vip,
                         'url': original_url,
                         'action': 'get_all_episodes',
                         'folder': folder, 'poster': image2,
                         'banner': '0', 'fanart': fanart2, 'content': content, 'imdb': imdb, 'tvdb': tvdb, 'tmdb': '0',
                         'title': title, 'originaltitle': title, 'tvshowtitle': tvshowtitle, 'year': year,
                         'premiered': premiered, 'season': season, 'episode': episode})
                    added_all_episodes = True

                self.list.append(
                    {'name': name, 'vip': vip, 'url': url, 'action': action, 'folder': folder, 'poster': image2,
                     'banner': '0', 'fanart': fanart2, 'content': content, 'imdb': imdb, 'tvdb': tvdb, 'tmdb': '0',
                     'title': title, 'originaltitle': title, 'tvshowtitle': tvshowtitle, 'year': year,
                     'premiered': premiered, 'season': season, 'episode': episode})
            except:
                pass

        return self.list

    def get_all_episodes(self, url):
        result = cache.get(client.request, 0, url)

        if result.strip().startswith('#EXTM3U') and '#EXTINF' in result:
            result = re.compile('#EXTINF:.+?\,(.+?)\n(.+?)\n', re.MULTILINE | re.DOTALL).findall(result)
            result = ['<item><title>%s</title><link>%s</link></item>' % (i[0], i[1]) for i in result]
            result = ''.join(result)

        try:
            r = base64.b64decode(result)
        except:
            r = ''
        if '</link>' in r:
            result = r

        result = str(result)

        result = self.account_filter(result)

        items = re.compile(
            '((?:<item>.+?</item>|<dir>.+?</dir>|<plugin>.+?</plugin>|<info>.+?</info>|'
            '<name>[^<]+</name><link>[^<]+</link><thumbnail>[^<]+</thumbnail><mode>[^<]+</mode>|'
            '<name>[^<]+</name><link>[^<]+</link><thumbnail>[^<]+</thumbnail><date>[^<]+</date>))',
            re.MULTILINE | re.DOTALL).findall(result)

        list = []
        for item in items:
            url = self.bob_get_tag_content(item, 'link', '0')

            if url is not '0':
                list.extend(self.bob_list(url))
        self.list = list
        self.worker()
        self.add_directory(self.list)
        return self.list

    @staticmethod
    def account_filter(result):
        if control.setting('ustvnow_email') == '' or control.setting('ustvnow_pass') == '':
            result = re.sub('http(?:s|)://(?:www\.|)ustvnow\.com/.+?<', '<', result)

        if control.setting('streamlive_user') == '' or control.setting('streamlive_pass') == '':
            result = re.sub('http(?:s|)://(?:www\.|)streamlive\.to/.+?<', '<', result)

        return result

    def worker(self):
        if not control.setting('metadata') == 'true':
            return

        self.imdb_info_link = 'http://www.omdbapi.com/?i=%s&plot=full&r=json'
        self.tvmaze_info_link = 'http://api.tvmaze.com/lookup/shows?thetvdb=%s'
        self.lang = 'en'

        self.meta = []
        total = len(self.list)

        for i in range(0, total):
            self.list[i].update({'metacache': False})
        self.list = metacache.fetch(self.list, self.lang)

        for r in range(0, total, 50):
            threads = []
            for i in range(r, r + 50):
                if i <= total:
                    threads.append(workers.Thread(self.movie_info, i))
                if i <= total:
                    threads.append(workers.Thread(self.tv_info, i))
            [i.start() for i in threads]
            [i.join() for i in threads]

        if len(self.meta) > 0:
            metacache.insert(self.meta)

    def movie_info(self, i):
        try:
            if self.list[i]['metacache'] is True:
                raise Exception()

            if not self.list[i]['content'] == 'movies':
                raise Exception()

            imdb = self.list[i]['imdb']
            if imdb == '0':
                raise Exception()

            url = self.imdb_info_link % imdb

            item = client.request(url, timeout='10')
            item = json.loads(item)

            if 'Error' in item and 'incorrect imdb' in item['Error'].lower():
                return self.meta.append(
                    {'imdb': imdb, 'tmdb': '0', 'tvdb': '0', 'lang': self.lang, 'item': {'code': '0'}})

            title = item['Title']
            title = title.encode('utf-8')
            if not title == '0':
                self.list[i].update({'title': title})

            year = item['Year']
            year = year.encode('utf-8')
            if not year == '0':
                self.list[i].update({'year': year})

            imdb = item['imdbID']
            if imdb is None or imdb == '' or imdb == 'N/A':
                imdb = '0'
            imdb = imdb.encode('utf-8')
            if not imdb == '0':
                self.list[i].update({'imdb': imdb, 'code': imdb})

            premiered = item['Released']
            if premiered is None or premiered == '' or premiered == 'N/A':
                premiered = '0'
            premiered = re.findall('(\d*) (.+?) (\d*)', premiered)
            try:
                premiered = '%s-%s-%s' % (premiered[0][2],
                                          {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                                           'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11',
                                           'Dec': '12'}[premiered[0][1]], premiered[0][0])
            except:
                premiered = '0'
            premiered = premiered.encode('utf-8')
            if not premiered == '0':
                self.list[i].update({'premiered': premiered})

            genre = item['Genre']
            if genre is None or genre == '' or genre == 'N/A':
                genre = '0'
            genre = genre.replace(', ', ' / ')
            genre = genre.encode('utf-8')
            if not genre == '0':
                self.list[i].update({'genre': genre})

            duration = item['Runtime']
            if duration is None or duration == '' or duration == 'N/A':
                duration = '0'
            duration = re.sub('[^0-9]', '', str(duration))
            duration = duration.encode('utf-8')
            if not duration == '0':
                self.list[i].update({'duration': duration})

            rating = item['imdbRating']
            if rating is None or rating == '' or rating == 'N/A' or rating == '0.0':
                rating = '0'
            rating = rating.encode('utf-8')
            if not rating == '0':
                self.list[i].update({'rating': rating})

            votes = item['imdbVotes']
            try:
                votes = str(format(int(votes), ',d'))
            except:
                pass
            if votes is None or votes == '' or votes == 'N/A':
                votes = '0'
            votes = votes.encode('utf-8')
            if not votes == '0':
                self.list[i].update({'votes': votes})

            mpaa = item['Rated']
            if mpaa is None or mpaa == '' or mpaa == 'N/A':
                mpaa = '0'
            mpaa = mpaa.encode('utf-8')
            if not mpaa == '0':
                self.list[i].update({'mpaa': mpaa})

            director = item['Director']
            if director is None or director == '' or director == 'N/A':
                director = '0'
            director = director.replace(', ', ' / ')
            director = re.sub(r'\(.*?\)', '', director)
            director = ' '.join(director.split())
            director = director.encode('utf-8')
            if not director == '0':
                self.list[i].update({'director': director})

            writer = item['Writer']
            if writer is None or writer == '' or writer == 'N/A':
                writer = '0'
            writer = writer.replace(', ', ' / ')
            writer = re.sub(r'\(.*?\)', '', writer)
            writer = ' '.join(writer.split())
            writer = writer.encode('utf-8')
            if not writer == '0':
                self.list[i].update({'writer': writer})

            cast = item['Actors']
            if cast is None or cast == '' or cast == 'N/A':
                cast = '0'
            cast = [x.strip() for x in cast.split(',') if not x == '']
            try:
                cast = [(x.encode('utf-8'), '') for x in cast]
            except:
                cast = []
            if not cast:
                cast = '0'
            if not cast == '0':
                self.list[i].update({'cast': cast})

            plot = item['Plot']
            if plot is None or plot == '' or plot == 'N/A':
                plot = '0'
            plot = client.replaceHTMLCodes(plot)
            plot = plot.encode('utf-8')
            if not plot == '0':
                self.list[i].update({'plot': plot})

            self.meta.append({'imdb': imdb, 'tmdb': '0', 'tvdb': '0', 'lang': self.lang,
                              'item': {'title': title, 'year': year, 'code': imdb, 'imdb': imdb, 'premiered': premiered,
                                       'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes,
                                       'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast,
                                       'plot': plot}})
        except:
            pass

    def tv_info(self, i):
        try:
            if self.list[i]['metacache'] is True:
                raise Exception()

            if not self.list[i]['content'] in ['tvshows', 'seasons', 'episodes']:
                raise Exception()

            tvdb = self.list[i]['tvdb']
            if tvdb == '0':
                raise Exception()

            url = self.tvmaze_info_link % tvdb

            item = client.request(url, output='response', error=True, timeout='10')

            if item[0] == '404':
                return self.meta.append(
                    {'imdb': '0', 'tmdb': '0', 'tvdb': tvdb, 'lang': self.lang, 'item': {'code': '0'}})

            item = json.loads(item[1])

            tvshowtitle = item['name']
            tvshowtitle = tvshowtitle.encode('utf-8')
            if not tvshowtitle == '0':
                self.list[i].update({'tvshowtitle': tvshowtitle})

            year = item['premiered']
            year = re.findall('(\d{4})', year)[0]
            year = year.encode('utf-8')
            if not year == '0':
                self.list[i].update({'year': year})

            try:
                imdb = item['externals']['imdb']
            except:
                imdb = '0'
            if imdb == '' or imdb is None:
                imdb = '0'
            imdb = imdb.encode('utf-8')
            if self.list[i]['imdb'] == '0' and not imdb == '0':
                self.list[i].update({'imdb': imdb})

            studio = item['network']['name']
            if studio == '' or studio is None:
                studio = '0'
            studio = studio.encode('utf-8')
            if not studio == '0':
                self.list[i].update({'studio': studio})

            genre = item['genres']
            if genre == '' or genre is None or genre == []:
                genre = '0'
            genre = ' / '.join(genre)
            genre = genre.encode('utf-8')
            if not genre == '0':
                self.list[i].update({'genre': genre})

            try:
                duration = str(item['runtime'])
            except:
                duration = '0'
            if duration == '' or duration is None:
                duration = '0'
            duration = duration.encode('utf-8')
            if not duration == '0':
                self.list[i].update({'duration': duration})

            rating = str(item['rating']['average'])
            if rating == '' or rating is None:
                rating = '0'
            rating = rating.encode('utf-8')
            if not rating == '0':
                self.list[i].update({'rating': rating})

            plot = item['summary']
            if plot == '' or plot is None:
                plot = '0'
            plot = re.sub('\n|<.+?>|</.+?>|.+?#\d*:', '', plot)
            plot = plot.encode('utf-8')
            if not plot == '0':
                self.list[i].update({'plot': plot})

            self.meta.append({'imdb': imdb, 'tmdb': '0', 'tvdb': tvdb, 'lang': self.lang,
                              'item': {'tvshowtitle': tvshowtitle, 'year': year, 'code': imdb, 'imdb': imdb,
                                       'tvdb': tvdb, 'studio': studio, 'genre': genre, 'duration': duration,
                                       'rating': rating, 'plot': plot}})
        except:
            pass

    @staticmethod
    def add_directory(items, mode=True, parent_url=None):
        if items is None or len(items) == 0:
            return

        system_addon = sys.argv[0]
        addon_poster = addon_banner = control.addonInfo('icon')
        addon_fanart = control.addonInfo('fanart')

        try:
            devmode = True if 'testings.xml' in control.listDir(control.dataPath)[1] else False
        except:
            devmode = False

        if mode is True:
            mode = [i['content'] for i in items if 'content' in i]
        else:
            mode = []
        if 'movies' in mode:
            mode = 'movies'
        elif 'tvshows' in mode:
            mode = 'tvshows'
        elif 'seasons' in mode:
            mode = 'seasons'
        elif 'episodes' in mode:
            mode = 'episodes'
        else:
            mode = None

        for i in items:
            try:
                try:
                    name = control.lang(int(i['name'])).encode('utf-8')
                except:
                    name = i['name']

                url = '%s?action=%s' % (system_addon, i['action'])
                try:
                    url += '&url=%s' % urllib.quote_plus(i['url'])
                except:
                    pass
                try:
                    url += '&content=%s' % urllib.quote_plus(i['content'])
                except:
                    pass

                if i['action'] == 'plugin' and 'url' in i:
                    url = i['url']

                try:
                    devurl = dict(urlparse.parse_qsl(urlparse.urlparse(url).query))['action']
                except:
                    devurl = None
                if devurl == 'developer' and devmode is not True:
                    raise Exception()

                poster = i['poster'] if 'poster' in i else '0'
                banner = i['banner'] if 'banner' in i else '0'
                fanart = i['fanart'] if 'fanart' in i else '0'
                if poster == '0':
                    poster = addon_poster
                if banner == '0' and poster == '0':
                    banner = addon_banner
                elif banner == '0':
                    banner = poster

                content = i['content'] if 'content' in i else '0'

                folder = i['folder'] if 'folder' in i else True

                meta = dict((k, v) for k, v in i.iteritems() if not v == '0')
                try:
                    meta.update({'duration': str(int(meta['duration']) * 60)})
                except:
                    pass

                cm = []

                if content in ['movies', 'tvshows']:
                    meta.update({'trailer': '%s?action=trailer&name=%s' % (system_addon, urllib.quote_plus(name))})
                    cm.append((control.lang(30707).encode('utf-8'),
                               'RunPlugin(%s?action=trailer&name=%s)' % (system_addon, urllib.quote_plus(name))))

                if content in ['movies', 'tvshows', 'seasons', 'episodes']:
                    cm.append((control.lang(30708).encode('utf-8'), 'XBMC.Action(Info)'))

                if content == 'movies':
                    try:
                        dfile = '%s (%s)' % (data['title'], data['year'])
                    except:
                        dfile = name
                elif content == 'episodes':
                    try:
                        dfile = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode']))
                    except:
                        dfile = name

                if mode == 'movies':
                    cm.append(
                        (control.lang(30711).encode('utf-8'),
                         'RunPlugin(%s?action=addView&content=movies)' % system_addon))
                elif mode == 'tvshows':
                    cm.append((control.lang(30712).encode('utf-8'),
                               'RunPlugin(%s?action=addView&content=tvshows)' % system_addon))
                    if parent_url:
                        cm.append(('Queue TV Show',
                                   'RunPlugin(%s?action=queueItem&url=%s)' % (
                                       system_addon, urllib.quote_plus(i['url']))))
                elif mode == 'seasons':
                    cm.append((control.lang(30713).encode('utf-8'),
                               'RunPlugin(%s?action=addView&content=seasons)' % system_addon))
                    if parent_url:
                        cm.append(('Queue Season',
                                   'RunPlugin(%s?action=queueItem&url=%s)' % (
                                       system_addon, urllib.quote_plus(i['url']))))
                elif mode == 'episodes':
                    cm.append((control.lang(30714).encode('utf-8'),
                               'RunPlugin(%s?action=addView&content=episodes)' % system_addon))

                if devmode is True:
                    try:
                        cm.append(('Open in browser',
                                   'RunPlugin(%s?action=browser&url=%s)' % (system_addon, urllib.quote_plus(i['url']))))
                    except:
                        pass
                if folder is not True:
                    cm.append(('Queue Item',
                               'RunPlugin(%s?action=queueItem&url=%s&name=%s&image=%s)' % (
                                   system_addon, urllib.quote_plus(i['url']), name, poster)))

                if xbmc.PlayList(xbmc.PLAYLIST_VIDEO).size() > 0:
                    cm.append(('Start Playing Queue',
                               'RunPlugin(%s?action=playQueue)' % (
                                   system_addon)))

                    cm.append(('Show Queue',
                               'Action("Playlist")'))

                    cm.append(('Clear Queue',
                               'RunPlugin(%s?action=clearQueue)' % (
                                   system_addon)))

                item = control.item(label=name, iconImage=poster, thumbnailImage=poster)

                try:
                    item.setArt({'poster': poster, 'tvshow.poster': poster, 'season.poster': poster, 'banner': banner,
                                 'tvshow.banner': banner, 'season.banner': banner})
                except:
                    pass

                if not fanart == '0':
                    item.setProperty('Fanart_Image', fanart)
                elif addon_fanart is not None:
                    item.setProperty('Fanart_Image', addon_fanart)

                item.setInfo(type='Video', infoLabels=meta)
                item.addContextMenuItems(cm)
                control.addItem(handle=int(sys.argv[1]), url=url, listitem=item, isFolder=folder)
            except:
                pass

        if mode is not None:
            control.content(int(sys.argv[1]), mode)
        control.directory(int(sys.argv[1]), cacheToDisc=True)
        if mode is not None:
            views.setView(mode)


class Resolver:
    def browser(self, url):
        try:
            url = self.get(url)
            if url is False:
                return
            control.execute(
                'RunPlugin(plugin://plugin.program.chrome.launcher/?url=%s&mode=showSite&stopPlayback=no)' % urllib.quote_plus(
                    url))
        except:
            pass

    def link(self, url):
        try:
            url = self.get(url)
            if url is False:
                return

            control.execute('ActivateWindow(busydialog)')
            url = self.process(url)
            control.execute('Dialog.Close(busydialog)')

            if url is None:
                return control.infoDialog(control.lang(30705).encode('utf-8'))
            return url
        except:
            pass

    @staticmethod
    def get(url, name=None, link = None):
        try:
            if name is None:
                name = control.infoLabel('listitem.label')
            items = re.compile('<sublink>(.+?)</sublink>').findall(url)
            if len(items) == 0:
                items = [url]
            items = [('Link %s' % (int(items.index(i)) + 1), i) for i in items]

            if len(items) == 1:
                url = items[0][1]
            elif link is not None:
                url = items[link][1]
            else:
                select = control.selectDialog([i[0] for i in items], name)
                if select == -1:
                    return False
                else:
                    url = items[select][1]

            return url
        except:
            pass

    @staticmethod
    def f4m(url, name):
        try:
            if not any(i in url for i in ['.f4m', '.ts']):
                raise Exception()
            ext = url.split('?')[0].split('&')[0].split('|')[0].rsplit('.')[-1].replace('/', '').lower()
            if ext not in ['f4m', 'ts']:
                raise Exception()

            params = urlparse.parse_qs(url)

            try:
                proxy = params['proxy'][0]
            except:
                proxy = None

            try:
                proxy_use_chunks = json.loads(params['proxy_for_chunks'][0])
            except:
                proxy_use_chunks = True

            try:
                maxbitrate = int(params['maxbitrate'][0])
            except:
                maxbitrate = 0

            try:
                simple_downloader = json.loads(params['simpledownloader'][0])
            except:
                simple_downloader = False

            try:
                auth_string = params['auth'][0]
            except:
                auth_string = ''

            try:
                streamtype = params['streamtype'][0]
            except:
                streamtype = 'TSDOWNLOADER' if ext == 'ts' else 'HDS'

            try:
                swf = params['swf'][0]
            except:
                swf = None

            from F4mProxy import f4mProxyHelper
            return f4mProxyHelper().playF4mLink(url, name, proxy, proxy_use_chunks, maxbitrate, simple_downloader,
                                                auth_string, streamtype, False, swf)
        except:
            pass

    @staticmethod
    def process(url, direct=True, name = ''):
        try:
            if not any(i in url for i in ['.jpg', '.png', '.gif']):
                raise Exception()
            ext = url.split('?')[0].split('&')[0].split('|')[0].rsplit('.')[-1].replace('/', '').lower()
            if ext not in ['jpg', 'png', 'gif']:
                raise Exception()
            try:
                i = os.path.join(control.dataPath, 'img')
                control.deleteFile(i)
                f = control.openFile(i, 'w')
                f.write(client.request(url))
                f.close()
                control.execute('ShowPicture("%s")' % i)
                return False
            except:
                return
        except:
            pass

        try:
            r = urllib.unquote_plus(url)
            if '</regex>' not in r:
                raise Exception()

            from resources.lib.modules import regex
            r = regex.resolve(r)

            if r[0] == 'makelist':
                Indexer().getx(r[1])
                return False
            elif r[0] == 'link':
                u = r[1]

            if u is not None:
                url = u
        except:
            pass

        try:
            if not url.startswith('rtmp'):
                raise Exception()
            if len(re.compile('\s*timeout=(\d*)').findall(url)) == 0:
                url += ' timeout=10'
            return url
        except:
            pass

        try:
            if not any(i in url for i in ['.m3u8', '.f4m', '.ts']):
                raise Exception()
            ext = url.split('?')[0].split('&')[0].split('|')[0].rsplit('.')[-1].replace('/', '').lower()
            if ext not in ['m3u8', 'f4m', 'ts']:
                raise Exception()
            return url
        except:
            pass

        try:
            preset = re.findall('<preset>(.+?)</preset>', url)[0]

            title, year, imdb = re.findall('<title>(.+?)</title>', url)[0], re.findall('<year>(.+?)</year>', url)[0], \
                                re.findall('<imdb>(.+?)</imdb>', url)[0]

            try:
                tvdb, tvshowtitle, premiered, season, episode = re.findall('<tvdb>(.+?)</tvdb>', url)[0], \
                                                                re.findall('<tvshowtitle>(.+?)</tvshowtitle>', url)[0], \
                                                                re.findall('<premiered>(.+?)</premiered>', url)[0], \
                                                                re.findall('<season>(.+?)</season>', url)[0], \
                                                                re.findall('<episode>(.+?)</episode>', url)[0]
            except:
                tvdb = tvshowtitle = premiered = season = episode = None

            direct = False

            preset_dictionary = ['primewire_mv_tv', 'watchfree_mv_tv', 'movie4k_mv', 'movie25_mv', 'watchseries_tv',
                                 'pftv_tv',
                                 'afdah_mv', 'dayt_mv', 'dizibox_tv', 'dizigold_tv', 'genvideo_mv', 'mfree_mv',
                                 'miradetodo_mv', 'movieshd_mv_tv', 'onemovies_mv_tv', 'onlinedizi_tv',
                                 'pelispedia_mv_tv',
                                 'pubfilm_mv_tv', 'putlocker_mv_tv', 'rainierland_mv', 'sezonlukdizi_tv',
                                 'tunemovie_mv',
                                 'xmovies_mv']

            if preset == 'searchsd':
                preset_dictionary = ['primewire_mv_tv', 'watchfree_mv_tv', 'movie4k_mv', 'movie25_mv',
                                     'watchseries_tv', 'pftv_tv']

            from resources.lib.sources import sources

            dialog = None
            dialog = control.progressDialog
            dialog.create(control.addonInfo('name'), control.lang(30726).encode('utf-8'))
            dialog.update(0)

            try:
                dialog.update(0, control.lang(30726).encode('utf-8') + ' ' + name, control.lang(30731).encode('utf-8'))
            except:
                pass

            u = sources().getSources(title, year, imdb, tvdb, season, episode, tvshowtitle, premiered,
                                     presetDict=preset_dictionary, progress=False, timeout=20)

            try:
                dialog.update(50, control.lang(30726).encode('utf-8') + ' ' + name, control.lang(30731).encode('utf-8'))
            except:
                pass

            u = sources().sourcesDirect(u, progress=False)

            if u is not None:
                try:
                    dialog.close()
                except:
                    pass
                return u
        except:
            try:
                dialog.close()
            except:
                pass

        try:
            from resources.lib.sources import sources

            u = sources().getURISource(url)

            if u is not False:
                direct = False
            if u is None or u is False or u == []:
                raise Exception()

            dialog = None
            dialog = control.progressDialog
            dialog.create(control.addonInfo('name'), control.lang(30726).encode('utf-8'))
            dialog.update(0)

            try:
                dialog.update(50, control.lang(30726).encode('utf-8') + ' ' + name, control.lang(30731).encode('utf-8'))
            except:
                pass

            u = sources().sourcesDirect(u, progress=False)

            if u is not None:
                try:
                    dialog.close()
                except:
                    pass
                return u
        except:
            try:
                dialog.close()
            except:
                pass

        try:
            if '.google.com' not in url:
                raise Exception()
            from resources.lib.modules import directstream
            u = directstream.google(url)[0]['url']
            return u
        except:
            pass

        try:
            if 'filmon.com/' not in url:
                raise Exception()
            from resources.lib.modules import filmon
            u = filmon.resolve(url)
            return u
        except:
            pass

        try:
            import urlresolver

            hmf = urlresolver.HostedMediaFile(url=url, include_disabled=True, include_universal=False)

            if hmf.valid_url() is False:
                raise Exception()

            direct = False
            u = hmf.resolve()

            if u is not False:
                return u
        except:
            pass

        try:
            try:
                headers = dict(urlparse.parse_qsl(url.rsplit('|', 1)[1]))
            except:
                headers = dict('')
            if not url.startswith('http'):
                raise Exception()
            result = client.request(url.split('|')[0], headers=headers, output='headers', timeout='20')
            if 'Content-Type' in result and 'html' not in result['Content-Type']:
                raise Exception()

            import liveresolver

            if liveresolver.isValid(url) is False:
                raise Exception()

            direct = False
            u = liveresolver.resolve(url)

            if u is not None:
                return u
        except:
            pass

        if direct is True:
            return url


# noinspection PyPep8Naming
class Player(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self)

    def play(self, url, content=None):
        try:
            url = Resolver().get(url)
            if url is False:
                return

            control.execute('ActivateWindow(busydialog)')
            url = Resolver().process(url)
            control.execute('Dialog.Close(busydialog)')

            if url is None:
                return control.infoDialog(control.lang(30705).encode('utf-8'))
            if url is False:
                return

            meta = {}
            for i in ['title', 'originaltitle', 'tvshowtitle', 'year', 'season', 'episode', 'genre', 'rating', 'votes',
                      'director', 'writer', 'plot', 'tagline']:
                try:
                    meta[i] = control.infoLabel('listitem.%s' % i)
                except:
                    pass
            meta = dict((k, v) for k, v in meta.iteritems() if not v == '')
            if 'title' not in meta:
                meta['title'] = control.infoLabel('listitem.label')
            icon = control.infoLabel('listitem.icon')

            self.name = meta['title']
            self.year = meta['year'] if 'year' in meta else '0'

            self.getbookmark = True if (content == 'movies' or content == 'episodes') else False

            self.offset = Bookmarks().get(self.name, self.year)

            f4m = Resolver().f4m(url, self.name)
            if f4m is not None:
                return

            item = control.item(path=url, iconImage=icon, thumbnailImage=icon)
            try:
                item.setArt({'icon': icon})
            except:
                pass
            item.setInfo(type='Video', infoLabels=meta)

            if 'plugin' in control.infoLabel('Container.PluginName'):
                if self.isPlaying():
                    xbmc.PlayList(xbmc.PLAYLIST_VIDEO).clear()
                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                playlist.add(url, item, 0)
                control.player.play(playlist, item)

            control.resolve(int(sys.argv[1]), True, item)

            self.totalTime = 0
            self.currentTime = 0

            for i in range(0, 240):
                if self.isPlaying():
                    break
                control.sleep(1000)
            while self.isPlaying():
                try:
                    self.totalTime = self.getTotalTime()
                    self.currentTime = self.getTime()
                except:
                    pass
                control.sleep(2000)
            control.sleep(5000)
        except:
            pass

    def onPlayBackStarted(self):
        control.execute('Dialog.Close(all,true)')
        if self.getbookmark is True and not self.offset == '0':
            self.seekTime(float(self.offset))

    def onPlayBackStopped(self):
        if self.getbookmark is True:
            Bookmarks().reset(self.currentTime, self.totalTime, self.name, self.year)
        xbmc.PlayList(xbmc.PLAYLIST_VIDEO).clear()

    def onPlayBackEnded(self):
        if self.getbookmark is True:
            Bookmarks().reset(self.currentTime, self.totalTime, self.name, self.year)


class Bookmarks:
    def get(self, name, year='0'):
        try:
            offset = '0'

            # if not control.setting('Bookmarks') == 'true': raise Exception()

            id_file = hashlib.md5()
            for i in name:
                id_file.update(str(i))
            for i in year:
                id_file.update(str(i))
            id_file = str(id_file.hexdigest())

            dbcon = database.connect(control.bookmarksFile)
            dbcur = dbcon.cursor()
            dbcur.execute("SELECT * FROM bookmark WHERE idFile = '%s'" % id_file)
            match = dbcur.fetchone()
            self.offset = str(match[1])
            dbcon.commit()

            if self.offset == '0':
                raise Exception()

            minutes, seconds = divmod(float(self.offset), 60)
            hours, minutes = divmod(minutes, 60)
            label = '%02d:%02d:%02d' % (hours, minutes, seconds)
            label = (control.lang(32502) % label).encode('utf-8')

            try:
                yes = control.dialog.contextmenu([label, control.lang(32501).encode('utf-8'), ])
            except:
                yes = control.yesnoDialog(label, '', '', str(name), control.lang(32503).encode('utf-8'),
                                          control.lang(32501).encode('utf-8'))

            if yes:
                self.offset = '0'

            return self.offset
        except:
            return offset

    @staticmethod
    def reset(current_time, total_time, name, year='0'):
        try:
            # if not control.setting('Bookmarks') == 'true': raise Exception()

            time_in_seconds = str(current_time)
            ok = int(current_time) > 180 and (current_time / total_time) <= .92

            id_file = hashlib.md5()
            for i in name:
                id_file.update(str(i))
            for i in year:
                id_file.update(str(i))
            id_file = str(id_file.hexdigest())

            control.makeFile(control.dataPath)
            dbcon = database.connect(control.bookmarksFile)
            dbcur = dbcon.cursor()
            dbcur.execute(
                "CREATE TABLE IF NOT EXISTS bookmark (""idFile TEXT, ""timeInSeconds TEXT, ""UNIQUE(idFile)"");")
            dbcur.execute("DELETE FROM bookmark WHERE idFile = '%s'" % id_file)
            if ok:
                dbcur.execute("INSERT INTO bookmark Values (?, ?)", (id_file, time_in_seconds))
            dbcon.commit()
        except:
            pass
