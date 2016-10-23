import datetime
import json
import os
import re
from threading import Event

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

import nanscrapers
import xbmc
import xbmcaddon
import xbmcvfs
import random

from executor import execute

scraper_cache = {}


class HostedLink:
    def __init__(self, title, year, imdb=None, tvdb=None, host=None, include_disabled=False, timeout=30):
        self.title = title
        self.year = year
        self.imdb = imdb
        self.tvdb = tvdb
        self.host = host
        self.timeout = timeout
        self.__scrapers = self.__get_scrapers(include_disabled)
        random.shuffle(self.__scrapers)
        xbmcvfs.mkdir(xbmc.translatePath(xbmcaddon.Addon("script.module.nanscrapers").getAddonInfo('profile')))
        self.cache_location = os.path.join(
            xbmc.translatePath(xbmcaddon.Addon("script.module.nanscrapers").getAddonInfo('profile')).decode('utf-8'),
            'url_cache.db')

    def __get_scrapers(self, include_disabled):
        klasses = nanscrapers.relevant_scrapers(self.host, include_disabled)
        scrapers = []
        for klass in klasses:
            if klass in scraper_cache:
                scrapers.append(scraper_cache[klass])
            else:
                scraper_cache[klass] = klass()
                scrapers.append(scraper_cache[klass])
        return scrapers

    def scrape_movie(self, maximum_age=60):
        scrape_f = lambda p: self.get_url(p, self.title, self.year, '', '', self.imdb, self.tvdb, "movie",
                                          self.cache_location, maximum_age)
        if len(self.__scrapers) > 0:
            pool_size = 10
            populator = lambda: execute(scrape_f, self.__scrapers, Event(), pool_size, self.timeout)
            return populator
        else:
            return False

    def scrape_episode(self, season, episode, maximum_age=60):
        scrape_f = lambda p: self.get_url(p, self.title, self.year, season, episode, self.imdb, self.tvdb, "episode",
                                          self.cache_location, maximum_age)
        if len(self.__scrapers) > 0:
            pool_size = 10
            populator = lambda: execute(scrape_f, self.__scrapers, Event(), pool_size, self.timeout)
            return populator
        else:
            return False

    @staticmethod
    def get_url(scraper, title, year, season, episode, imdb, tvdb, type, cache_location, maximum_age):
        try:
            dbcon = database.connect(cache_location)
            dbcur = dbcon.cursor()
            dbcur.execute(
                "CREATE TABLE IF NOT EXISTS rel_src (""scraper TEXT, ""title Text, year TEXT, ""season TEXT, ""episode TEXT, ""imdb_id TEXT, ""urls TEXT, ""added TEXT, ""UNIQUE(scraper, title, year, season, episode)"");")
        except:
            pass

        try:
            sources = []
            dbcur.execute(
                "SELECT * FROM rel_src WHERE scraper = '%s' AND title = '%s' AND year = '%s' AND season = '%s' AND episode = '%s'" % (
                    scraper.name, title.upper(), year, season, episode))
            match = dbcur.fetchone()
            t1 = int(re.sub('[^0-9]', '', str(match[7])))
            t2 = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
            update = abs(t2 - t1) > maximum_age
            if update == False:
                sources = json.loads(match[6])
                return sources
        except:
            pass

        try:
            sources = []
            if type == "movie":
                sources = scraper.scrape_movie(title, year, imdb)
            elif type == "episode":
                sources = scraper.scrape_episode(title, year, season, episode, imdb, tvdb)
            if sources == None:
                sources = []
            else:
                dbcur.execute(
                    "DELETE FROM rel_src WHERE scraper = '%s' AND title = '%s' AND year = '%s' AND season = '%s' AND episode = '%s'" % (
                        scraper.name, title.upper(), year, season, episode))
                dbcur.execute("INSERT INTO rel_src Values (?, ?, ?, ?, ?, ?, ?, ?)", (
                    scraper.name, title.upper(), year, season, episode, imdb, json.dumps(sources), datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
                dbcon.commit()

            return sources
        except:
            pass
