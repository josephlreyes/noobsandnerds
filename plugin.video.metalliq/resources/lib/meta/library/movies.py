import os
import json
import urllib

from xbmcswift2 import xbmc, xbmcvfs

from meta import plugin, import_tmdb, LANG
from meta.utils.text import date_to_timestamp
from meta.library.tools import scan_library, add_source
from meta.utils.rpc import RPC
from meta.gui import dialogs
from meta.navigation.base import get_icon_path, get_background_path

from language import get_string as _
from settings import SETTING_MOVIES_LIBRARY_FOLDER, SETTING_MOVIES_PLAYLIST_FOLDER, SETTING_LIBRARY_SET_DATE

@plugin.cached(TTL=60*2)
def query_movies_server(url):
    response = urllib.urlopen(url)
    return json.loads(response.read())

def update_library():
    # setup library folder
    library_folder = plugin.get_setting(SETTING_MOVIES_LIBRARY_FOLDER)
    if not xbmcvfs.exists(library_folder):
        return
    scan_library(type="video")

def add_movie_to_library(library_folder, src, id, date):    
    changed = False
    
    # create movie folder
    movie_folder = os.path.join(library_folder, str(id)+'/')
    if not xbmcvfs.exists(movie_folder):
        try: 
            xbmcvfs.mkdir(movie_folder)
        except:
            pass

    # create nfo file
    nfo_filepath = os.path.join(movie_folder, str(id)+".nfo")
    if not xbmcvfs.exists(nfo_filepath):
        changed = True
        nfo_file = xbmcvfs.File(nfo_filepath, 'w')
        if src == "imdb":
            content = "http://www.imdb.com/title/%s/" % str(id)
        else:
            content = "http://www.themoviedb.org/movie/%s" % str(id)
        nfo_file.write(content)
        nfo_file.close()
        if date and plugin.get_setting(SETTING_LIBRARY_SET_DATE, converter=bool):
            os.utime(nfo_filepath, (date,date))
        
    # create strm file
    strm_filepath = os.path.join(movie_folder, str(id)+".strm")
    if not xbmcvfs.exists(strm_filepath):
        changed = True
        strm_file = xbmcvfs.File(strm_filepath, 'w')
        content = plugin.url_for("movies_play", src=src, id=id, mode='library')
        strm_file.write(content)
        strm_file.close()
        if date and plugin.get_setting(SETTING_LIBRARY_SET_DATE, converter=bool):
            os.utime(strm_filepath, (date,date))
    xbmc.executebuiltin("RunScript(script.qlickplay,info=afteradd)")
#    xbmc.executebuiltin("RunScript(script.artworkdownloader,mediatype=movie,dbid=%s)" % xbmc.getInfoLabel('ListItem.DBID'))
    
    return changed

def setup_library(library_folder):
    if library_folder[-1] != "/":
        library_folder += "/"
    playlist_folder = plugin.get_setting(SETTING_MOVIES_PLAYLIST_FOLDER, converter=str)
    if plugin.get_setting(SETTING_MOVIES_PLAYLIST_FOLDER, converter=str)[-1] != "/": playlist_folder += "/"
    # create folders
    if not xbmcvfs.exists(playlist_folder): xbmcvfs.mkdir(playlist_folder)
    if not xbmcvfs.exists(library_folder):
        # create folder
        xbmcvfs.mkdir(library_folder)
        # auto configure folder
        msg = _("Would you like to automatically set [COLOR ff0084ff]M[/COLOR]etalli[COLOR ff0084ff]Q[/COLOR] as a movies video source?")
        if dialogs.yesno(_("Library setup"), msg):
            source_thumbnail = get_icon_path("movies")
            
            source_name = "[COLOR ff0084ff]M[/COLOR]etalli[COLOR ff0084ff]Q[/COLOR] Movies"
            
            source_content = "('{0}','movies','metadata.themoviedb.org','',2147483647,1,'<settings><setting id=\"RatingS\" value=\"TMDb\" /><setting id=\"certprefix\" value=\"Rated \" /><setting id=\"fanart\" value=\"true\" /><setting id=\"keeporiginaltitle\" value=\"false\" /><setting id=\"language\" value=\"{1}\" /><setting id=\"tmdbcertcountry\" value=\"us\" /><setting id=\"trailer\" value=\"true\" /></settings>',0,0,NULL,NULL)".format(library_folder, LANG)

            add_source(source_name, library_folder, source_content, source_thumbnail)

    # return translated path
    return xbmc.translatePath(library_folder)

def auto_movie_setup(library_folder):
    if library_folder[-1] != "/":
        library_folder += "/"
    playlist_folder = plugin.get_setting(SETTING_MOVIES_PLAYLIST_FOLDER, converter=str)
    if plugin.get_setting(SETTING_MOVIES_PLAYLIST_FOLDER, converter=str)[-1] != "/": playlist_folder += "/"
    # create folders
    if not xbmcvfs.exists(playlist_folder): xbmcvfs.mkdir(playlist_folder)
    if not xbmcvfs.exists(library_folder):
        xbmcvfs.mkdir(library_folder)
        source_thumbnail = get_icon_path("movies")
        source_name = "[COLOR ff0084ff]M[/COLOR]etalli[COLOR ff0084ff]Q[/COLOR] Movies"
        source_content = "('{0}','movies','metadata.themoviedb.org','',2147483647,1,'<settings><setting id=\"RatingS\" value=\"TMDb\" /><setting id=\"certprefix\" value=\"Rated \" /><setting id=\"fanart\" value=\"true\" /><setting id=\"keeporiginaltitle\" value=\"false\" /><setting id=\"language\" value=\"{1}\" /><setting id=\"tmdbcertcountry\" value=\"us\" /><setting id=\"trailer\" value=\"true\" /></settings>',0,0,NULL,NULL)".format(library_folder, LANG)
        add_source(source_name, library_folder, source_content, source_thumbnail)

