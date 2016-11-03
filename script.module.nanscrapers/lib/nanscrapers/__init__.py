import xbmc
import xbmcaddon
import os
from hl import HostedLink
from scraper import Scraper
from scraperplugins import *


def scrape_movie(title, year, imdb, host=None, include_disabled=False, timeout=30):
    return HostedLink(title, year, imdb, None, host, include_disabled, timeout).scrape_movie()


def scrape_episode(title, year, season, episode, imdb, tvdb, host=None, include_disabled=False, timeout=30):
    return HostedLink(title, year, imdb, tvdb, host, include_disabled, timeout).scrape_episode(season, episode)

def scrape_song(title, artist, host=None, include_disabled=False, timeout=30):
    return HostedLink(title, None, None, None, host, include_disabled, timeout).scrape_song(title, artist)


def relevant_scrapers(names_list=None, include_disabled=False):
    if names_list is None:
        names_list = ["ALL"]
    if type(names_list) is not list:
        names_list = [names_list]

    classes = Scraper.__class__.__subclasses__(Scraper)
    relevant = []

    for index,domain in enumerate(names_list):
        if isinstance(domain, basestring) and not domain == "ALL":
            names_list[index] = domain.lower()

    for scraper in classes:
        if include_disabled or scraper._is_enabled():
            if names_list == ["ALL"] or (
                    any(name in scraper.name.lower() for name in names_list)):
                relevant.append(scraper)
    return relevant


def clear_cache():
    try:
        from sqlite3 import dbapi2 as database
    except:
        from pysqlite2 import dbapi2 as database

    cache_location = os.path.join(
        xbmc.translatePath(xbmcaddon.Addon("script.module.nanscrapers").getAddonInfo('profile')).decode('utf-8'),
        'url_cache.db')

    dbcon = database.connect(cache_location)
    dbcur = dbcon.cursor()

    try:
        dbcur.execute("DROP TABLE IF EXISTS rel_src")
        dbcur.execute("DROP TABLE IF EXISTS rel_music_src")
        dbcur.execute("VACUUM")
        dbcon.commit()
    except:
        pass


def _update_settings_xml():
    settings_location = os.path.join(xbmcaddon.Addon('script.module.nanscrapers').getAddonInfo('path'), 'resources',
                                     'settings.xml')
    try:
        os.makedirs(os.path.dirname(settings_location))
    except OSError:
        pass

    new_xml = [
        '<?xml version="1.0" encoding="utf-8" standalone="yes"?>',
        '<settings>',
        '\t<category label="Scrapers 1">'
    ]

    scrapers = sorted(relevant_scrapers(include_disabled=True), key=lambda x: x.name.lower())

    category_number = 2
    category_scraper_number = 0
    for scraper in scrapers:
        if category_scraper_number > 50:
            new_xml.append('\t</category>')
            new_xml.append('\t<category label="Scrapers %s">' % (category_number))
            category_number += 1
            category_scraper_number = 0
        new_xml.append('\t\t<setting label="%s" type="lsep"/>' % (scraper.name))
        scraper_xml = scraper.get_settings_xml()
        new_xml += ['\t\t' + line for line in scraper_xml]
        category_scraper_number += len(scraper_xml) + 1

    new_xml.append('\t</category>')
    new_xml.append('</settings>')

    try:
        with open(settings_location, 'r') as f:
            old_xml = f.read()
    except:
        old_xml = ''

    new_xml = '\n'.join(new_xml)
    if old_xml != new_xml:
        try:
            with open(settings_location, 'w') as f:
                f.write(new_xml)
        except:
            raise


_update_settings_xml()
