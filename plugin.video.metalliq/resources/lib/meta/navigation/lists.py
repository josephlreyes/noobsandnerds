import os
from xbmcswift2 import xbmc, xbmcplugin, xbmcvfs
from xbmcswift2.listitem import ListItem
from meta import plugin
from meta.navigation.movies import make_movie_item
from meta.info import get_tvshow_metadata_trakt, get_season_metadata_trakt, get_episode_metadata_trakt, get_trakt_movie_metadata
from meta.navigation.base import get_icon_path, get_background_path
from meta.navigation.movies import make_movie_item, movies_add_to_library
from meta.navigation.tvshows import make_tvshow_item, tv_play, tv_season, tv_add_to_library
from meta.gui import dialogs
from meta.utils.text import to_utf8
from language import get_string as _
from trakt import trakt
from settings import SETTING_TRAKT_PER_PAGE, SETTING_FORCE_VIEW, SETTING_LIST_VIEW

SORT = [xbmcplugin.SORT_METHOD_UNSORTED, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_DATE, xbmcplugin.SORT_METHOD_VIDEO_YEAR, xbmcplugin.SORT_METHOD_LABEL, xbmcplugin.SORT_METHOD_UNSORTED]
FORCE = plugin.get_setting(SETTING_FORCE_VIEW, bool)
VIEW  = plugin.get_setting(SETTING_LIST_VIEW, int)

@plugin.route('/lists')
def lists():
    """ Lists directory """
    items = [
        {
            'label': _("Liked lists"),
            'path': plugin.url_for("lists_trakt_liked_lists", page = 1),
            'icon': get_icon_path("traktlikedlists"),
        },
        {
            'label': _("My lists"),
            'path': plugin.url_for("lists_trakt_my_lists"),
            'icon': get_icon_path("traktmylists"),
        },
        {
            'label': _("Search list"),
            'path': plugin.url_for("lists_trakt_search_for_lists"),
            'icon': get_icon_path("search"),
        },
    ]
    fanart = plugin.addon.getAddonInfo('fanart')
    for item in items:
        item['properties'] = {'fanart_image' : get_background_path()}
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items

@plugin.route('/lists/trakt/liked_lists/<page>', options = {"page": "1"})
def lists_trakt_liked_lists(page):
    lists, pages = trakt.trakt_get_liked_lists(page)
    items = []
    for list in lists:
        info = list["list"]
        name = info["name"]
        user = info["user"]["username"]
        slug = info["ids"]["slug"]
        items.append({
            'label': name,
            'path': plugin.url_for("lists_trakt_show_list", user = user, slug = slug),
            'context_menu': [
                (
                    _("Add list to library"),
                    "RunPlugin({0})".format(plugin.url_for("lists_trakt_add_all_to_library", user=user, slug=slug))
                )
            ],
            'icon': get_icon_path("traktlikedlists"),
        })
    if pages > page:
        items.append({
            'label': _("Next >>"),
            'path': plugin.url_for("lists_trakt_liked_lists", page = int(page) + 1),
            'icon': get_icon_path("traktlikedlists"),
        })
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/lists/trakt/my_lists')
def lists_trakt_my_lists():
    lists = trakt.trakt_get_lists()
    items = []
    for list in lists:
        name = list["name"]
        user = list["user"]["username"]
        slug = list["ids"]["slug"]
        items.append({
            'label': name,
            'path': plugin.url_for(lists_trakt_show_list, user = user, slug = slug),
            'context_menu': [
                (
                    _("Add list to library"),
                    "RunPlugin({0})".format(plugin.url_for("lists_trakt_add_all_to_library", user=user, slug=slug))
                )
            ],
            'icon': get_icon_path("traktmylists"),
        })
        fanart = plugin.addon.getAddonInfo('fanart')
        for item in items:
            item['properties'] = {'fanart_image' : get_background_path()}
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/lists/trakt_search_for_lists')
def lists_trakt_search_for_lists():
    term = plugin.keyboard(heading=_("search for"))
    return lists_search_for_lists_term(term, 1)

@plugin.route('/lists/search_for_lists_term/<term>/<page>')
def lists_search_for_lists_term(term,page):
    lists, pages = trakt.search_for_list(term, page)
    page = int(page)
    pages = int(pages)
    items = []
    for list in lists:
        if "list" in list:
            list_info = list["list"]
        else:
            continue
        name = list_info["name"]
        user = list_info["username"]
        slug = list_info["ids"]["slug"]

        info = {}
        info['title'] = name
        if "description" in list_info:
            info["plot"] = list_info["description"]
        else:
            info["plot"] = _("No description available")
        if user != None:
            items.append({
                'label': "{0} {1} {2}".format(to_utf8(name), _("by"), to_utf8(user)),
                'path': plugin.url_for("lists_trakt_show_list", user=user, slug=slug),
                'context_menu': [
                    (
                        _("Add list to library"),
                        "RunPlugin({0})".format(plugin.url_for("lists_trakt_add_all_to_library", user=user, slug=slug))
                    )
                ],
                'info': info,
                'icon': get_icon_path("traktlikedlists"),
            })
            fanart = plugin.addon.getAddonInfo('fanart')
            for item in items:
                item['properties'] = {'fanart_image' : get_background_path()}
    if (len(items) < plugin.get_setting(SETTING_TRAKT_PER_PAGE, int) and pages > page):
        page = page + 1
        results = lists_search_for_lists_term(term, page)
        return items + results
    if pages > page:
        items.append({
            'label': _("Next page").format() + "  >>  (%s/%s)" % (page + 1, pages),
            'path': plugin.url_for("lists_search_for_lists_term", term = term, page=page + 1),
            'icon': get_icon_path("traktlikedlists"),
        })
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/lists/trakt/list_to_library/<user>/<slug>')
def lists_trakt_add_all_to_library(user, slug):
    items = lists_trakt_show_list(user, slug)
    tv_ids = []
    movie_ids = []
    for item in items:
        if not isinstance(item, type):
            if "/tv/" in str(item):
                if "/tv/play/" in str(item):
                    pre_tvdb = str(item).split(" (plugin://plugin.video.metalliq/tv/play/")
                    pro_tvdb = str(pre_tvdb[1]).split("/")
                    tvdb = str(pro_tvdb[0])
                    if not tvdb in tv_ids: tv_ids.append(tvdb)
                elif "/tv/tvdb/" in str(item):
                    pre_tvdb = str(item).split(" (plugin://plugin.video.metalliq/tv/tvdb/")
                    if "/" in str(pre_tvdb[1]): pro_tvdb = str(pre_tvdb[1]).split("/")
                    else: pro_tvdb = str(pre_tvdb[1]).split(")")
                    tvdb = str(pro_tvdb[0])
                    if not tvdb in tv_ids: tv_ids.append(tvdb)
            elif "/movies/" in str(item):
                if "/tmdb/" in str(item):
                    pre_tmdb = str(item).split(" (plugin://plugin.video.metalliq/movies/play/tmdb/")
                    pro_tmdb = str(pre_tmdb[1]).split("/")
                    tmdb = str(pro_tmdb[0])
                    if not tmdb in movie_ids: movie_ids.append(tmdb)
                elif "/imdb/" in str(item):
                    pre_imdb = str(item).split(" (plugin://plugin.video.metalliq/movies/play/imdb/")
                    pro_imdb = str(pre_imdb[1]).split("/")
                    imdb = str(pro_imdb[0])
                    if not imdb in movie_ids: movie_ids.append(imdb)
        else:
            if "tvshowtitle" in str(item["info"]):
                if item["info"]["tvdb_id"] != None and item["info"]["tvdb_id"] != "" and str(item["info"]["tvdb_id"]) not in tv_ids: tv_ids.append(str(item["info"]["tvdb_id"]))
                elif item["info"]["imdb_id"] != None and item["info"]["imdb_id"] != "" and str(item["info"]["imdb_id"]) not in tv_ids: tv_ids.append(str(item["info"]["imdb_id"]))
            else:
                if item["info"]["tmdb"] != None and item["info"]["tmdb"] != "" and str(item["info"]["tmdb"]) not in movie_ids: movie_ids.append(str(item["info"]["tmdb"]))
                elif item["info"]["imdb_id"] != None and item["info"]["imdb_id"] != "" and str(item["info"]["imdb_id"]) not in movie_ids: movie_ids.append(str(item["info"]["imdb_id"]))
    if len(tv_ids) > 0:
        shows_list_file_path = "special://profile/addon_data/plugin.video.metalliq/shows_from_" + slug + "_by_" + user + ".txt"
        shows_import_file_path = "special://profile/addon_data/plugin.video.metalliq/shows_to_add.txt"
        if xbmcvfs.exists(shows_list_file_path): os.remove(xbmc.translatePath(shows_import_file_path))
        if xbmcvfs.exists(shows_import_file_path): os.remove(xbmc.translatePath(shows_import_file_path))
        tv_id_list = ""
        for id in tv_ids:
            tv_id_list = tv_id_list + str(id) + '\n'
        if not xbmcvfs.exists(shows_list_file_path):
            batch_add_file = xbmcvfs.File(shows_list_file_path, 'w')
            batch_add_file.write(tv_id_list)
            batch_add_file.close()
        if not xbmcvfs.exists(shows_import_file_path):
            batch_add_file = xbmcvfs.File(shows_import_file_path, 'w')
            batch_add_file.write(tv_id_list)
            batch_add_file.close()
        plugin.notify(msg='TVShows, seasons & episodes', title='Converted to list.txt', delay=3000, image=get_icon_path("tvshows"))
    if len(movie_ids) > 0:
        movies_list_file_path = "special://profile/addon_data/plugin.video.metalliq/movies_from_" + slug + "_by_" + user + ".txt"
        movies_import_file_path = "special://profile/addon_data/plugin.video.metalliq/movies_to_add.txt"
        if xbmcvfs.exists(movies_list_file_path): os.remove(xbmc.translatePath(movies_import_file_path))
        if xbmcvfs.exists(movies_import_file_path): os.remove(xbmc.translatePath(movies_import_file_path))
        movie_id_list = ""
        for id in movie_ids:
            movie_id_list = movie_id_list + str(id) + '\n'
        if not xbmcvfs.exists(movies_list_file_path):
            batch_add_file = xbmcvfs.File(movies_list_file_path, 'w')
            batch_add_file.write(movie_id_list)
            batch_add_file.close()
        if not xbmcvfs.exists(movies_import_file_path):
            batch_add_file = xbmcvfs.File(movies_import_file_path, 'w')
            batch_add_file.write(movie_id_list)
            batch_add_file.close()
        plugin.notify(msg='Movies', title='Converted to list.txt', delay=3000, image=get_icon_path("movies"))
    plugin.notify(msg='Generating', title='.strm-files', delay=3000, image=get_icon_path("metalliq"))
    xbmc.executebuiltin("RunPlugin(plugin://plugin.video.metalliq/movies/batch_add_to_library)")

@plugin.route('/lists/trakt/show_list/<user>/<slug>')
def lists_trakt_show_list(user, slug):
    list_items = trakt.get_list(user, slug)
    return _lists_trakt_show_list(list_items)

@plugin.route('/lists/trakt/_show_list/<list_items>')
def _lists_trakt_show_list(list_items):
    genres_dict = trakt.trakt_get_genres("tv")
    if type(list_items) == str:
        import urllib
        list_items = eval(urllib.unquote(list_items))
    items = []
    for list_item in list_items:
        item = None
        item_type = list_item["type"]
        if item_type == "show":
            tvdb_id = list_item["show"]["ids"]["tvdb"]
            show = list_item["show"]
            info = get_tvshow_metadata_trakt(show, genres_dict)
            context_menu = [
                (
                    _("Add to library"),
                    "RunPlugin({0})".format(plugin.url_for("tv_add_to_library", id=tvdb_id))
                ),
                (
                    _("Show info"), 'Action(Info)'
                ),
                (
                    _("Remove from list"),
                    "RunPlugin({0})".format(plugin.url_for("lists_remove_show_from_list", src="tvdb", id=tvdb_id))
                )
            ]
            item = ({
                'label': info['title'],
                'path': plugin.url_for("tv_tvshow", id=tvdb_id),
                'context_menu': context_menu,
                'thumbnail': info['poster'],
                'icon': get_icon_path("tv"),
                'poster': info['poster'],
                'properties' : {'fanart_image' : info['fanart']},
                'info_type': 'video',
                'stream_info': {'video': {}},
                'info': info
            })
        elif item_type == "season":
            tvdb_id = list_item["show"]["ids"]["tvdb"]
            season = list_item["season"]
            show = list_item["show"]
            show_info = get_tvshow_metadata_trakt(show, genres_dict)
            season_info = get_season_metadata_trakt(show_info,season, genres_dict)
            label = "{0} - Season {1}".format(to_utf8(show["title"]),season["number"])
            context_menu = [
                (
                    _("Add to library"),
                    "RunPlugin({0})".format(plugin.url_for("tv_add_to_library", id=tvdb_id))
                ),
                (
                    _("Show info"), 'Action(Info)'
                ),
                (
                    _("Remove from list"),
                    "RunPlugin({0})".format(plugin.url_for("lists_remove_season_from_list", src="tvdb",
                                                           id=tvdb_id, season=list_item["season"]["number"]))
                )
            ]
            item = ({
                'label': label,
                'path': plugin.url_for(tv_season, id=tvdb_id, season_num=list_item["season"]["number"]),
                'context_menu': context_menu,
                'info': season_info,
                'thumbnail': season_info['poster'],
                'icon': get_icon_path("tv"),
                'poster': season_info['poster'],
                'properties': {'fanart_image': season_info['fanart']},
            })
        elif item_type == "episode":
            tvdb_id = list_item["show"]["ids"]["tvdb"]
            episode = list_item["episode"]
            show = list_item["show"]
            season_number = episode["season"]
            episode_number = episode["number"]
            show_info = get_tvshow_metadata_trakt(show, genres_dict)
            episode_info = get_episode_metadata_trakt(show_info, episode)
            label = "{0} - S{1}E{2} - {3}".format(show_info["title"], season_number,
                                                  episode_number, episode_info["title"])
            context_menu = [
                (
                    _("Select stream..."),
                    "PlayMedia({0})".format(
                        plugin.url_for("tv_play", id=tvdb_id, season=season_number,
                                       episode=episode_number, mode='select'))
                ),
                (
                    _("Show info"),
                    'Action(Info)'
                ),
                (
                    _("Add to list"),
                    "RunPlugin({0})".format(plugin.url_for("lists_add_episode_to_list", src='tvdb', id=tvdb_id,
                                                           season=season_number, episode=episode_number))
                ),
                (
                    _("Remove from list"),
                    "RunPlugin({0})".format(plugin.url_for("lists_remove_season_from_list", src="tvdb", id=tvdb_id,
                                                           season=season_number, episode = episode_number))
                )
            ]
            item = ({
                'label': label,
                'path': plugin.url_for("tv_play", id=tvdb_id, season=season_number,
                                       episode=episode_number, mode='default'),
                'context_menu': context_menu,
                'info': episode_info,
                'is_playable': True,
                'info_type': 'video',
                'stream_info': {'video': {}},
                'thumbnail': episode_info['poster'],
                'poster': episode_info['poster'],
                'icon': get_icon_path("tv"),
                'properties': {'fanart_image': episode_info['fanart']},
                      })
        elif item_type == "movie":
            movie = list_item["movie"]
            movie_info = get_trakt_movie_metadata(movie)
            item = make_movie_item(movie_info, True)
        if item is not None:
            items.append(item)
    for item in items:
        item['properties'] = {'fanart_image' : get_background_path()}
    if FORCE == True: return plugin.finish(items=items, sort_methods=SORT, view_mode=VIEW)
    else: return plugin.finish(items=items, sort_methods=SORT)

@plugin.route('/lists/add_movie_to_list/<src>/<id>')
def lists_add_movie_to_list(src, id):
    selected = get_list_selection()
    if selected is not None:
        user = selected['user']
        slug = selected['slug']
        if (src == "tmdb" or src == "trakt"): #trakt seems to want integers unless imdb
            id = int(id)
        data = {
            "movies": [
                {
                    "ids": {
                        src: id
                    }
                }
            ]
        }
        trakt.add_to_list(user, slug, data)

@plugin.route('/lists/add_show_to_list/<src>/<id>')
def lists_add_show_to_list(src, id):
    selected = get_list_selection()
    if selected is not None:
        user = selected['user']
        slug = selected['slug']
        if src == "tvdb" or src == "trakt":  # trakt seems to want integers
            id = int(id)
        data = {
            "shows": [
                {
                    "ids": {
                        src: id
                    }
                }
            ]
        }
        trakt.add_to_list(user, slug, data)

@plugin.route('/lists/add_season_to_list/<src>/<id>/<season>')
def lists_add_season_to_list(src, id, season):
    selected = get_list_selection()
    if selected is not None:
        user = selected['user']
        slug = selected['slug']
        if src == "tvdb" or src == "trakt":  # trakt seems to want integers
            season = int(season)
            id = int(id)
        data = {
            "shows": [
                {
                    "seasons": [
                        {
                            "number": season,
                        }
                    ],
                    "ids": {
                        src: id
                    }
                }
            ]
        }
        trakt.add_to_list(user, slug, data)

@plugin.route('/lists/add_episode_to_list/<src>/<id>/<season>/<episode>')
def lists_add_episode_to_list(src, id, season, episode):
    selected = get_list_selection()
    if selected is not None:
        user = selected['user']
        slug = selected['slug']
        if src == "tvdb" or src == "trakt": #trakt seems to want integers
            season = int(season)
            episode = int(episode)
            id = int(id)
        data = {
                "shows": [
                    {
                        "seasons": [
                            {
                                "number": season,
                                "episodes": [
                                    {
                                        "number": episode
                                    }
                                ]
                            }
                        ],
                        "ids": {
                            src: id
                        }
                    }
                ]
            }
        trakt.add_to_list(user, slug, data)

@plugin.route('/lists/remove_movie_from_list/<src>/<id>')
def lists_remove_movie_from_list(src, id):
    selected = get_list_selection()
    if selected is not None:
        user = selected['user']
        slug = selected['slug']
        if (src == "tmdb" or src == "trakt"):  # trakt seems to want integers unless imdb
            id = int(id)
        data = {
            "movies": [
                {
                    "ids": {
                        src: id
                    }
                }
            ]
        }
        trakt.remove_from_list(user, slug, data)

@plugin.route('/lists/remove_show_from_list/<src>/<id>')
def lists_remove_show_from_list(src, id):
    selected = get_list_selection()
    if selected is not None:
        user = selected['user']
        slug = selected['slug']
        if src == "tvdb" or src == "trakt":  # trakt seems to want integers
            id = int(id)
        data = {
            "shows": [
                {
                    "ids": {
                        src: id
                    }
                }
            ]
        }
        trakt.remove_from_list(user, slug, data)

@plugin.route('/lists/remove_season_from_list/<src>/<id>/<season>')
def lists_remove_season_from_list(src, id, season):
    selected = get_list_selection()
    if selected is not None:
        user = selected['user']
        slug = selected['slug']
        if src == "tvdb" or src == "trakt":  # trakt seems to want integers
            season = int(season)
            id = int(id)
        data = {
            "shows": [
                {
                    "seasons": [
                        {
                            "number": season,
                        }
                    ],
                    "ids": {
                        src: id
                    }
                }
            ]
        }
        trakt.remove_from_list(user, slug, data)

@plugin.route('/lists/remove_episode_from_list/<src>/<id>/<season>/<episode>')
def lists_remove_episode_from_list(src, id, season, episode):
    selected = get_list_selection()
    if selected is not None:
        user = selected['user']
        slug = selected['slug']
        if src == "tvdb" or src == "trakt":  # trakt seems to want integers
            season = int(season)
            episode = int(episode)
            id = int(id)
        data = {
            "shows": [
                {
                    "seasons": [
                        {
                            "number": season,
                            "episodes": [
                                {
                                    "number": episode
                                }
                            ]
                        }
                    ],
                    "ids": {
                        src: id
                    }
                }
            ]
        }
        trakt.remove_from_list(user, slug, data)

def get_list_selection():
    trakt_lists = trakt.trakt_get_lists()
    my_lists = []
    for list in trakt_lists:
        my_lists.append({
            'name': list["name"],
            'user': list["user"]["username"],
            'slug': list["ids"]["slug"]
        })
    selection = dialogs.select(_("Select list"), [l["name"] for l in my_lists])
    if selection >= 0:
        return my_lists[selection]
    return None
