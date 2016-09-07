import copy, os
from xbmcswift2 import xbmc, xbmcplugin, xbmcvfs
from meta import plugin, import_tmdb, LANG
from meta.info import get_movie_metadata, get_trakt_movie_metadata
from meta.gui import dialogs
from meta.utils.text import parse_year, date_to_timestamp, to_utf8
from meta.play.movies import play_movie, play_movie_from_guide
from meta.play.channelers import ADDON_STANDARD, ADDON_PICKER
from meta.play.players import ADDON_DEFAULT, ADDON_SELECTOR
from meta.library.movies import setup_library, add_movie_to_library, batch_add_movies_to_library
from meta.library.tools import scan_library
from meta.play.base import active_players, active_channelers
from meta.navigation.base import get_icon_path, get_genre_icon, get_background_path, get_base_genres, caller_name, caller_args
from language import get_string as _
from settings import CACHE_TTL, SETTING_MOVIES_LIBRARY_FOLDER, SETTING_MOVIES_PLAYED_BY_ADD, SETTING_FORCE_VIEW, SETTING_MOVIES_VIEW, SETTING_TRAKT_PER_PAGE, SETTING_MOVIES_BATCH_ADD_FILE_PATH, SETTING_TV_BATCH_ADD_FILE_PATH, SETTING_FORCE_VIEW, SETTING_MOVIES_VIEW, SETTING_MOVIES_DEFAULT_PLAYER_FROM_LIBRARY, SETTING_MOVIES_DEFAULT_AUTO_ADD

SORT = [xbmcplugin.SORT_METHOD_UNSORTED, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_DATE, xbmcplugin.SORT_METHOD_VIDEO_YEAR, xbmcplugin.SORT_METHOD_LABEL, xbmcplugin.SORT_METHOD_UNSORTED]
FORCE = plugin.get_setting(SETTING_FORCE_VIEW, bool)
VIEW  = plugin.get_setting(SETTING_MOVIES_VIEW, int)

@plugin.route('/movies')
def movies():
    """ Movies directory """
    items = [
        {
            'label': _("Search (Trakt)"),
            'path': plugin.url_for(trakt_movies_search, page='1'),
            'icon': get_icon_path("search"),
        },
        {
            'label': _("Personal (Trakt)"),
            'path': plugin.url_for(trakt_my_movies),
            'icon': get_icon_path("trakt"),
        },
        {
            'label': _("Most played (Trakt)"),
            'path': plugin.url_for(trakt_movies_played, page='1'),
            'icon': get_icon_path("player"),
        },
        {
            'label': _("Most watched (Trakt)"),
            'path': plugin.url_for(trakt_movies_watched, page='1'),
            'icon': get_icon_path("traktwatchlist"),
        },
        {
            'label': _("Most collected (Trakt)"),
            'path': plugin.url_for(trakt_movies_collected, page='1'),
            'icon': get_icon_path("traktcollection"),
        },
        {
            'label': _("Popular (Trakt)"),
            'path': plugin.url_for(trakt_movies_popular, page='1'),
            'icon': get_icon_path("traktrecommendations"),
        },
        {
            'label': _("Trending (Trakt)"),
            'path': plugin.url_for(trakt_movies_trending, page='1'),
            'icon': get_icon_path("trending"),
        },
        {
            'label': _("Search (TMDb)"),
            'path': plugin.url_for(tmdb_movies_search),
            'icon': get_icon_path("search"),
        },
        {
            'label': _("Blockbusters (TMDb)"),
            'path': plugin.url_for(tmdb_movies_blockbusters, page='1'),
            'icon': get_icon_path("most_voted"),
        },
        {
            'label': _("Genres (TMDb)"),
            'path': plugin.url_for(tmdb_movies_genres),
            'icon': get_icon_path("genres"),
        },
        {
            'label': _("In theatres (TMDb)"),
            'path': plugin.url_for(tmdb_movies_now_playing, page='1'),
            'icon': get_icon_path("intheatres"),
        },
        {
            'label': _("Popular (TMDb)"),
            'path': plugin.url_for(tmdb_movies_most_popular, page='1'),
            'icon': get_icon_path("popular"),
        },
        {
            'label': _("Top rated (TMDb)"),
            'path': plugin.url_for(tmdb_movies_top_rated, page='1'),
            'icon': get_icon_path("top_rated"),
        }
    ]
    fanart = plugin.addon.getAddonInfo('fanart')
    for item in items:
        item['properties'] = {'fanart_image' : get_background_path()}
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items

@plugin.route('/movies/trakt/search')
def trakt_movies_search():
    term = plugin.keyboard(heading=_("search for"))
    return trakt_movies_search_term(term, 1)

@plugin.route('/movies/trakt/search/<term>/<page>')
def trakt_movies_search_term(term, page):
    from trakt import trakt
    results, pages = trakt.search_for_movie_paginated(term, page)
    return list_trakt_movies_search_results_paginated(results, pages, page)

def list_trakt_movies_search_results_paginated(results, pages, page):
    from trakt import trakt
    results = sorted(results,key=lambda item: item["movie"]["title"].lower().replace("the ", ""))
    genres_dict = dict([(x['slug'], x['name']) for x in trakt.trakt_get_genres("movies")])
    movies = [get_trakt_movie_metadata(item["movie"], None) for item in results]
    items = [make_movie_item(movie) for movie in movies]
    nextpage = int(page) + 1
    if pages > page:
        items.append({
            'label': _("Next page").format() + "  >>  (%s/%s)" % (nextpage, pages),
            'path': plugin.url_for("trakt_movies_search", page=int(page) + 1),
            'icon': get_icon_path("item_next"),
        })
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/movies/trakt/personal')
def trakt_my_movies():
    """ Trakt movies directory """
    items = [
        {
            'label': _("Collection"),
            'path': plugin.url_for(trakt_movies_collection),
            'icon': get_icon_path("traktcollection"),
            'context_menu': [
                (
                    _("Add to library"),
                    "RunPlugin({0})".format(plugin.url_for(trakt_movies_collection_to_library))
                )
            ],
        },
        {
            'label': _("Watchlist"),
            'path': plugin.url_for(trakt_movies_watchlist),
            'icon': get_icon_path("traktwatchlist"),
            'context_menu': [
                (
                    _("Add to library"),
                    "RunPlugin({0})".format(plugin.url_for(trakt_movies_watchlist_to_library))
                )
            ],
        },
        {
            'label': _("Recommendations"),
            'path': plugin.url_for(movies_trakt_recommendations),
            'icon': get_icon_path("traktrecommendations"),
        }
    ]
    fanart = plugin.addon.getAddonInfo('fanart')
    for item in items:
        item['properties'] = {'fanart_image' : get_background_path()}
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items

@plugin.route('/movies/trakt/played/<page>')
def trakt_movies_played(page):
    from trakt import trakt
    results, pages = trakt.trakt_get_played_movies_paginated(page)
    return list_trakt_movies_played_paginated(results, pages, page)

def list_trakt_movies_played_paginated(results, pages, page):
    from trakt import trakt
    results = sorted(results,key=lambda item: item["movie"]["title"].lower().replace("the ", ""))
    genres_dict = dict([(x['slug'], x['name']) for x in trakt.trakt_get_genres("movies")])
    movies = [get_trakt_movie_metadata(item["movie"], genres_dict) for item in results]
    items = [make_movie_item(movie) for movie in movies]
    if int(pages) > int(page):
        items.append({
            'label': _("Next page").format() + "  >>  (%s/%s)" % (int(page) + 1, int(pages)),
            'path': plugin.url_for("trakt_movies_played", page=int(page) + 1),
            'icon': get_icon_path("item_next"),
        })
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/movies/trakt/watched/<page>')
def trakt_movies_watched(page):
    from trakt import trakt
    results, pages = trakt.trakt_get_watched_movies_paginated(page)
    return list_trakt_movies_watched_paginated(results, pages, page)

def list_trakt_movies_watched_paginated(results, pages, page):
    from trakt import trakt
    results = sorted(results,key=lambda item: item["movie"]["title"].lower().replace("the ", ""))
    genres_dict = dict([(x['slug'], x['name']) for x in trakt.trakt_get_genres("movies")])
    movies = [get_trakt_movie_metadata(item["movie"], genres_dict) for item in results]
    items = [make_movie_item(movie) for movie in movies]
    if int(pages) > int(page):
        items.append({
            'label': _("Next page").format() + "  >>  (%s/%s)" % (int(page) + 1, int(pages)),
            'path': plugin.url_for("trakt_movies_watched", page=int(page) + 1),
            'icon': get_icon_path("item_next"),
        })
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/movies/trakt/collected/<page>')
def trakt_movies_collected(page):
    from trakt import trakt
    results, pages = trakt.trakt_get_collected_movies_paginated(page)
    return list_trakt_movies_collected_paginated(results, pages, page)

def list_trakt_movies_collected_paginated(results, pages, page):
    from trakt import trakt
    results = sorted(results,key=lambda item: item["movie"]["title"].lower().replace("the ", ""))
    genres_dict = dict([(x['slug'], x['name']) for x in trakt.trakt_get_genres("movies")])
    movies = [get_trakt_movie_metadata(item["movie"], genres_dict) for item in results]
    items = [make_movie_item(movie) for movie in movies]
    if int(pages) > int(page):
        items.append({
            'label': _("Next page").format() + "  >>  (%s/%s)" % (int(page) + 1, int(pages)),
            'path': plugin.url_for("trakt_movies_collected", page=int(page) + 1),
            'icon': get_icon_path("item_next"),
        })
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/movies/trakt/popular/<page>')
def trakt_movies_popular(page):
    from trakt import trakt
    results, pages = trakt.trakt_get_popular_movies_paginated(page)
    return list_trakt_movies_popular_paginated(results, pages, page)

def list_trakt_movies_popular_paginated(results, pages, page):
    from trakt import trakt
    results = sorted(results,key=lambda item: item["title"].lower().replace("the ", ""))
    genres_dict = dict([(x['slug'], x['name']) for x in trakt.trakt_get_genres("movies")])
    movies = [get_trakt_movie_metadata(item, genres_dict) for item in results]
    items = [make_movie_item(movie) for movie in movies]
    if int(pages) > int(page):
        items.append({
            'label': _("Next page").format() + "  >>  (%s/%s)" % (int(page) + 1, int(pages)),
            'path': plugin.url_for("trakt_movies_popular", page=int(page) + 1),
            'icon': get_icon_path("item_next"),
        })
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return items

@plugin.route('/movies/trakt/trending/<page>')
def trakt_movies_trending(page):
    from trakt import trakt
    results, pages = trakt.trakt_get_trending_movies_paginated(page)
    return list_trakt_movies_trending_paginated(results, pages, page)

def list_trakt_movies_trending_paginated(results, pages, page):
    from trakt import trakt
    results = sorted(results,key=lambda item: item["movie"]["title"].lower().replace("the ", ""))
    genres_dict = dict([(x['slug'], x['name']) for x in trakt.trakt_get_genres("movies")])
    movies = [get_trakt_movie_metadata(item["movie"], genres_dict) for item in results]
    items = [make_movie_item(movie) for movie in movies]
    if int(pages) > int(page):
        items.append({
            'label': _("Next page").format() + "  >>  (%s/%s)" % (int(page) + 1, int(pages)),
            'path': plugin.url_for("trakt_movies_trending", page=int(page) + 1),
            'icon': get_icon_path("item_next"),
        })
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/movies/tmdb/search')
def tmdb_movies_search():
    """ Activate movie search """
    term = plugin.keyboard(heading=_("search for"))
    return tmdb_movies_search_term(term, 1)

@plugin.route('/movies/tmdb/search_term/<term>/<page>')
def tmdb_movies_search_term(term, page):
    """ Perform search of a specified <term>"""
    import_tmdb()
    result = tmdb.Search().movie(query=term, language = LANG, page = page)
    items = list_tmdb_movies(result)
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/movies/tmdb/blockbusters/<page>')
def tmdb_movies_blockbusters(page):
    import_tmdb()
    result = tmdb.Discover().movie(language=LANG, **{'page': page, 'sort_by': 'revenue.desc'})
    items = list_tmdb_movies(result)
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/movies/tmdb/genres')
def tmdb_movies_genres():
    """ List all movie genres """
    genres = get_base_genres()
    items = sorted([{ 'label': name, 'icon': get_genre_icon(id), 'path': plugin.url_for(movies_genre, id=id, page='1')} for id, name in genres.items()], key=lambda k: k['label'])
    if FORCE == True: return plugin.finish(items=items, view_mode=VIEW)
    else: return plugin.finish(items=items)

@plugin.route('/movies/tmdb/now_playing/<page>')
def tmdb_movies_now_playing(page):
    import_tmdb()
    result = tmdb.Movies().now_playing(language=LANG, page=page)
    items = list_tmdb_movies(result)
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/movies/tmdb/most_popular/<page>')
def tmdb_movies_most_popular(page):
    """ Most popular movies """
    import_tmdb()    
    result = tmdb.Movies().popular(language=LANG, page=page)
    items = list_tmdb_movies(result)
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/movies/tmdb/top_rated/<page>')
def tmdb_movies_top_rated(page):
    import_tmdb()    
    result = tmdb.Movies().top_rated(language=LANG, page=page)
    items = list_tmdb_movies(result)
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/movies/trakt/personal/collection')
def trakt_movies_collection():
    from trakt import trakt
    result = trakt.trakt_get_collection("movies")
    items = list_trakt_movies(result)
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/movies/trakt/personal/watchlist')
def trakt_movies_watchlist():
    from trakt import trakt
    result = trakt.trakt_get_watchlist("movies")
    items = list_trakt_movies(result)
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/movies/trakt/personal/recommendations')
def movies_trakt_recommendations():
    from trakt import trakt
    genres_dict = dict([(x['slug'], x['name']) for x in trakt.trakt_get_genres("movies")])
    movies = trakt.get_recommendations("movies")
    items = []
    for movie in movies:
        items.append(make_movie_item(get_trakt_movie_metadata(movie, genres_dict)))
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/movies/genre/<id>/<page>')
def movies_genre(id, page):
    """ Movies by genre id """
    import_tmdb()
    result = tmdb.Genres(id).movies(id=id, language=LANG, page=page)
    items = list_tmdb_movies(result)
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/movies/trakt/collection_to_library')
def trakt_movies_collection_to_library():
    from trakt import trakt
    if dialogs.yesno(_("Add all to library"), _("Are you sure you want to add your entire Trakt collection to Kodi library?")):
        movies_add_all_to_library(trakt.trakt_get_collection("movies"))

@plugin.route('/movies/trakt/watchlist_to_library')
def trakt_movies_watchlist_to_library():
    from trakt import trakt
    if dialogs.yesno(_("Add all to library"), _("Are you sure you want to add your entire Trakt watchlist to Kodi library?")):
        movies_add_all_to_library(trakt.trakt_get_watchlist("movies"))

@plugin.route('/movies/set_library_player/<path>')
def set_movie_library_player(path):
    # get active players
    players = active_players("movies")
    players.insert(0, ADDON_SELECTOR)
    players.insert(0, ADDON_DEFAULT)
    # let the user select one player
    selection = dialogs.select(_("Select default player"), [p.title for p in players])
    if selection == -1:
        return
    # get selected player
    player = players[selection]
    # Create play with file
    player_filepath = os.path.join(path, 'player.info')
    player_file = xbmcvfs.File(player_filepath, 'w')
    content = "{0}".format(player.id)
    player_file.write(content)
    player_file.close()

def movies_add_all_to_library(items):
    library_folder = setup_library(plugin.get_setting(SETTING_MOVIES_LIBRARY_FOLDER))
    for item in items:
        ids = item["movie"]["ids"]
        if ids.get('imdb'):
            add_movie_to_library(library_folder, "imdb", ids["imdb"], None)
        elif ids.get('tmdb'):
            add_movie_to_library(library_folder, "tmdb", ids["tmdb"], None)
        else:
            plugin.log.error("movie %s is missing both imdb and tmdb ids" % ids['slug'])
    scan_library(type="video")

@plugin.route('/movies/add_to_library/<src>/<id>')
def movies_add_to_library(src, id):
    """ Add movie to library """
    library_folder = setup_library(plugin.get_setting(SETTING_MOVIES_LIBRARY_FOLDER))
    date = None
    if src == "tmdb":
        import_tmdb()
        movie = tmdb.Movies(id).info()
        date = date_to_timestamp(movie.get('release_date'))
        imdb_id = movie.get('imdb_id')
        if imdb_id:
            src = "imdb"
            id = imdb_id
    players = active_players("movies")
    if plugin.get_setting(SETTING_MOVIES_DEFAULT_AUTO_ADD, bool) == True:
        player = plugin.get_setting(SETTING_MOVIES_DEFAULT_PLAYER_FROM_LIBRARY, unicode)
    else:
        players.insert(0, ADDON_SELECTOR)
        players.insert(0, ADDON_DEFAULT)
        selection = dialogs.select(_("Play with..."), [p.title for p in players])
        if selection == -1:
            return
        player = players[selection]
    # setup library folder
    library_folder = setup_library(plugin.get_setting(SETTING_MOVIES_LIBRARY_FOLDER))
    # add to library
    if plugin.get_setting(SETTING_MOVIES_DEFAULT_AUTO_ADD, bool) == True:
        add_movie_to_library(library_folder, src, id, play_plugin=plugin.get_setting(SETTING_MOVIES_DEFAULT_PLAYER_FROM_LIBRARY, unicode))
    else:
        add_movie_to_library(library_folder, src, id, play_plugin=ADDON_DEFAULT.id)
    scan_library(type="video")

@plugin.route('/movies/batch_add_to_library')
def movies_batch_add_to_library():
    """ Batch add movies to library """
    movie_batch_file = plugin.get_setting(SETTING_MOVIES_BATCH_ADD_FILE_PATH)
    if xbmcvfs.exists(movie_batch_file):
        try:
            f = open(xbmc.translatePath(movie_batch_file), 'r')
            r = f.read()
            f.close()
            ids = r.split('\n')
        except: return plugin.notify(msg='Movies Batch Add File', title='Not found', delay=3000, image=get_icon_path("movies"))
        library_folder = setup_library(plugin.get_setting(SETTING_MOVIES_LIBRARY_FOLDER))
        import_tmdb()
        for id in ids:
            if "," in id:
                csvs = id.split(',')
                for csv in csvs:
                    if not str(csv).startswith("tt") and csv != "":
                        movie = tmdb.Movies(csv).info()
                        id = movie.get('imdb_id')
                    batch_add_movies_to_library(library_folder, id)
            else:
                if not str(id).startswith("tt") and id != "":
                    movie = tmdb.Movies(id).info()
                    id = movie.get('imdb_id')
                batch_add_movies_to_library(library_folder, id)
        os.remove(xbmc.translatePath(movie_batch_file))
        if xbmcvfs.exists(plugin.get_setting(SETTING_TV_BATCH_ADD_FILE_PATH)): 
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.metalliq/tv/batch_add_to_library)")
            return True
        else:
            xbmc.sleep(1000)
            plugin.notify(msg='Added movie strm-files', title='Starting library scan', delay=3000, image=get_icon_path("movies"))
            scan_library(type="video")
            return True
    elif xbmcvfs.exists(plugin.get_setting(SETTING_TV_BATCH_ADD_FILE_PATH)): xbmc.executebuiltin("RunPlugin(plugin://plugin.video.metalliq/tv/batch_add_to_library)")

@plugin.route('/movies/related/<id>')
def movies_related(id):
    import_tmdb()
    movie = tmdb.Movies(id).info()
    imdb_id = movie.get('imdb_id')
    from trakt import trakt
    results = trakt.trakt_get_related_movies_paginated(imdb_id)
    items = list_trakt_movies_related(results)
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

def list_trakt_movies_related(results):
    from trakt import trakt
    results = sorted(results,key=lambda item: item["title"].lower().replace("the ", ""))
    genres_dict = dict([(x['slug'], x['name']) for x in trakt.trakt_get_genres("movies")])
    movies = [get_trakt_movie_metadata(item, genres_dict) for item in results]
    items = [make_movie_item(movie) for movie in movies]
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/movies/play/<src>/<id>/<mode>')
def movies_play(src, id, mode="external"):
    import_tmdb()
    tmdb_id = None
    if src == "tmdb": tmdb_id = id
    elif src == "imdb":
        info = tmdb.Find(id).info(external_source="imdb_id")
        try: tmdb_id = info["movie_results"][0]["id"]
        except (KeyError, TypeError): pass
    if tmdb_id: play_movie(tmdb_id, mode)
    else: plugin.set_resolved_url()

@plugin.route('/movies/play_guide/<src>/<id>/<mode>')
def guide_movies_play(src, id, mode="external"):
    import_tmdb()
    tmdb_id = None
    if src == "tmdb": tmdb_id = id
    elif src == "imdb":
        info = tmdb.Find(id).info(external_source="imdb_id")
        try: tmdb_id = info["movie_results"][0]["id"]
        except (KeyError, TypeError): pass
    if tmdb_id: play_movie_from_guide(tmdb_id, mode)
    else: plugin.set_resolved_url()

def list_tmdb_movies(result):
    genres_dict = get_base_genres()
    movies = [get_movie_metadata(item, genres_dict) for item in result['results']]
    items = [make_movie_item(movie) for movie in movies]
    if 'page' in result:
        page = result['page']
        args = caller_args()
        if page < result['total_pages']:
            args['page'] = str(page + 1)
            items.append({
                'label': _("Next >>"),
                'icon': get_icon_path("item_next"),
                'path': plugin.url_for(caller_name(), **args)
            })
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

def list_trakt_movies(results):
    from trakt import trakt
    results = sorted(results,key=lambda item: item["movie"]["title"].lower().replace("the ", ""))
    genres_dict = dict([(x['slug'], x['name']) for x in trakt.trakt_get_genres("movies")])
    movies = [get_trakt_movie_metadata(item["movie"], genres_dict) for item in results]
    items = [make_movie_item(movie) for movie in movies]
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return items

@plugin.route('/movies/play_by_name/<name>/<lang>')
def movies_play_by_name(name, lang = "en"):
    """ Activate tv search """
    import_tmdb()
    from meta.utils.text import parse_year
    items = tmdb.Search().movie(query=name, language=lang, page=1)["results"]
    if not items: return dialogs.ok(_("Movie not found"), "{0} {1}".format(_("No movie information found on TMDB for"), name))
    if len(items) > 1:
        selection = dialogs.select(_("Choose Movie"), ["{0} ({1})".format(
            to_utf8(s["title"]),
            parse_year(s["release_date"])) for s in items])
    else: selection = 0
    if selection != -1:
        id = items[selection]["id"]
        movies_play("tmdb", id, "context")
        if plugin.get_setting(SETTING_MOVIES_PLAYED_BY_ADD, converter=bool) == True: movies_add_to_library("tmdb", id)

@plugin.route('/movies/play_by_name_guide/<name>/<lang>')
def guide_movies_play_by_name(name, lang = "en"):
    import_tmdb()
    from meta.utils.text import parse_year
    items = tmdb.Search().movie(query=name, language=lang, page=1)["results"]
    if not items: return dialogs.ok(_("Movie not found"), "{0} {1}".format(_("No movie information found on TMDB for"), name))
    if len(items) > 1:
        selection = dialogs.select(_("Choose Movie"), ["{0} ({1})".format(
            to_utf8(s["title"]),
            parse_year(s["release_date"])) for s in items])
    else: selection = 0
    if selection != -1:
        id = items[selection]["id"]
        guide_movies_play("tmdb", id, "default")
        if plugin.get_setting(SETTING_MOVIES_PLAYED_BY_ADD, converter=bool) == True: movies_add_to_library("tmdb", id)

def make_movie_item(movie_info, is_list = False):
    tmdb_id = movie_info.get('tmdb')
    imdb_id = movie_info.get('imdb')
    if tmdb_id:
        id = tmdb_id 
        src = 'tmdb'
    else:
        id = imdb_id 
        src = 'imdb'
    if xbmc.getCondVisibility("system.hasaddon(script.qlickplay)"): context_menu = [(_("Movie trailer"),"RunScript(script.qlickplay,info=playtrailer,id={0})".format(id)), (_("Add to library"),"RunPlugin({0})".format(plugin.url_for("movies_add_to_library", src=src, id=id))), (_("[COLOR ff0084ff]Q[/COLOR]lick[COLOR ff0084ff]P[/COLOR]lay"), "RunScript(script.qlickplay,info=movieinfo,id={0})".format(id)), (_("Recommended movies (TMDb)"),"ActivateWindow(10025,plugin://script.qlickplay/?info=similarmovies&id={0})".format(id))]
    elif xbmc.getCondVisibility("system.hasaddon(script.extendedinfo)"): context_menu = [(_("Movie trailer"),"RunScript(script.extendedinfo,info=playtrailer,id={0})".format(id)), (_("Add to library"),"RunPlugin({0})".format(plugin.url_for("movies_add_to_library", src=src, id=id))), (_("Extended movie info"), "RunScript(script.extendedinfo,info=extendedinfo,id={0})".format(id)), (_("Recommended movies (TMDb)"),"ActivateWindow(10025,plugin://script.extendedinfo/?info=similarmovies&id={0})".format(id))]
    else: context_menu = [(_("Add to library"),"RunPlugin({0})".format(plugin.url_for("movies_add_to_library", src=src, id=id)))]
    context_menu.append((_("Related Movies (Trakt)"),"ActivateWindow(10025,{0})".format(plugin.url_for("movies_related", id=id))))
    context_menu.append((_("Select stream..."),"PlayMedia({0})".format(plugin.url_for("movies_play", src=src, id=id, mode='select'))))
    context_menu.append((_("Add to list"),"RunPlugin({0})".format(plugin.url_for("lists_add_movie_to_list", src=src, id=id))))
    context_menu.append((_("Show info"),'Action(Info)'))
    if is_list:
        context_menu.append(
            (
                _("Remove from list"),
                "RunPlugin({0})".format(plugin.url_for("lists_remove_movie_from_list", src=src, id=id))
            )
        )
    return {
        'label': movie_info['title'],
        'path': plugin.url_for("movies_play", src=src, id=id, mode='default'),
        'context_menu': context_menu,
        'thumbnail': movie_info['poster'],
        'icon': "DefaultVideo.png",
        'poster': movie_info['poster'],
        'properties' : {'fanart_image' : movie_info['fanart']},
        'is_playable': True,
        'info_type': 'video',
        'stream_info': {'video': {}},
        'info': movie_info
    }
