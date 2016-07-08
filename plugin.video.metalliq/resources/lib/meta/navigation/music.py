import xbmcgui
from meta import plugin, LANG
from meta.gui import dialogs
from meta.utils.text import to_utf8
from meta.play.players import ADDON_DEFAULT, ADDON_SELECTOR
from meta.play.music import play_music, play_musicvideo
from meta.navigation.base import search, get_icon_path, get_background_path, get_genre_icon, get_genres, get_tv_genres, caller_name, caller_args
from meta.library.music import setup_library, add_music_to_library
from meta.library.tools import scan_library
from language import get_string as _
from settings import SETTING_MUSIC_LIBRARY_FOLDER, SETTING_PREFERRED_MUSIC_TYPE

from lastfm import lastfm


@plugin.route('/music')
def music():
    items = [
        {
            'label': _("Search"),
            'path': plugin.url_for("music_search"),
            'icon': get_icon_path("search"),
        },
        {
            'label': _("Top Artists"),
            'path': plugin.url_for("music_top_artists"),
            'icon': get_icon_path("top_rated"),
        },
        {
            'label': _("Top Tracks"),
            'path': plugin.url_for("music_top_tracks"),
            'icon': get_icon_path("trending"),
        },
        {
            'label': _("Top Artists (NL)"),
            'path': plugin.url_for("music_top_artists_by_country", country='netherlands'),
            'icon': get_icon_path("top_nl"),
        },
        {
            'label': _("Top Artists (UK)"),
            'path': plugin.url_for("music_top_artists_by_country", country='united kingdom'),
            'icon': get_icon_path("top_uk"),
        },
        {
            'label': _("Top Artists (US)"),
            'path': plugin.url_for("music_top_artists_by_country", country='united states'),
            'icon': get_icon_path("top_us"),
        },
        {
            'label': _("Top Artists (CA)"),
            'path': plugin.url_for("music_top_artists_by_country", country='canada'),
            'icon': get_icon_path("top_ca"),
        },
        {
            'label': _("Top Artists (AU)"),
            'path': plugin.url_for("music_top_artists_by_country", country='australia'),
            'icon': get_icon_path("top_au"),
        },
        {
            'label': _("Top Tracks (NL)"),
            'path': plugin.url_for("music_top_tracks_by_country", country='netherlands'),
            'icon': get_icon_path("trending_nl"),
        },
        {
            'label': _("Top Tracks (UK)"),
            'path': plugin.url_for("music_top_tracks_by_country", country='united kingdom'),
            'icon': get_icon_path("trending_uk"),
        },
        {
            'label': _("Top Tracks (US)"),
            'path': plugin.url_for("music_top_tracks_by_country", country='united states'),
            'icon': get_icon_path("trending_us"),
        },
        {
            'label': _("Top Tracks (CA)"),
            'path': plugin.url_for("music_top_tracks_by_country", country='canada'),
            'icon': get_icon_path("trending_ca"),
        },
        {
            'label': _("Top Tracks (AU)"),
            'path': plugin.url_for("music_top_tracks_by_country", country='australia'),
            'icon': get_icon_path("trending_au"),
        }
    ]

    fanart = plugin.addon.getAddonInfo('fanart')
    for item in items:
        item['properties'] = {'fanart_image' : get_background_path()}
        
    return items


@plugin.route('/music/search')
def music_search():
    items = [
        {
            'label': _("Search artist"),
            'path': plugin.url_for("music_search_artist"),
            'icon': get_icon_path("search"),
        },
        {
            'label': _("Search album"),
            'path': plugin.url_for("music_search_album"),
            'icon': get_icon_path("search"),
        },
        {
            'label': _("Search track"),
            'path': plugin.url_for("music_search_track"),
            'icon': get_icon_path("search"),
        }
    ]

    fanart = plugin.addon.getAddonInfo('fanart')
    for item in items:
        item['properties'] = {'fanart_image' : get_background_path()}
        
    return items


@plugin.route('/music/search/artist')
def music_search_artist():
    search(music_search_artist_term)


@plugin.route('/music/search/album')
def music_search_album():
    search(music_search_album_term)


@plugin.route('/music/search/track')
def music_search_track():
    search(music_search_track_term)


@plugin.route('/music/top_artists/<page>', options={'page': "1"})
def music_top_artists(page):
    results = lastfm.get_top_artists(page)
    artists = results["artists"]["artist"]
    items = []
    for artist in artists:
        large_image = artist["image"][-1]["#text"]
        name = to_utf8(artist["name"])
        context_menu = [
            (
                _("Add to library"),
                "RunPlugin({0})".format(plugin.url_for("music_add_artist_to_library", artist_name=name))
            )
        ]
        item = {
            'label': name,
            'path': plugin.url_for(music_artist_albums, artist_name=name),
            'thumbnail': large_image,
            'icon': "DefaultMusic.png",
            'poster': large_image,
            'info': {
                'artist': name,
            },
            'info_type': 'music',
            'context_menu': context_menu
        }
        items.append(item)
    return items



@plugin.route('/music/top_tracks/<page>', options={'page': "1"})
def music_top_tracks(page):
    results = lastfm.get_top_tracks(page)
    #plugin.notify(msg=_(SETTING_PREFERRED_MUSIC_TYPE), title=_(plugin.get_setting(SETTING_PREFERRED_MUSIC_TYPE)), delay=1000, image=get_icon_path("tv"))
    tracks = results["tracks"]["track"]
    items = []
    for track in tracks:
        large_image = track["image"][-1]["#text"]
        track_name = to_utf8(track["name"])
        artist_name = to_utf8(track["artist"]["name"])
        if plugin.get_setting(SETTING_PREFERRED_MUSIC_TYPE) == "audio":
            path = plugin.url_for(music_play_audio, artist_name=artist_name, track_name=track_name)
            icon = "DefaultMusic.png"
            info_type = "music"
            context_menu = [
                (
                    _("Context music player"),
                    "PlayMedia({0})".format(plugin.url_for("music_play_audio", artist_name=artist_name,
                                                           track_name=track_name, mode='context'))
                ),
                (
                    _("Add to library"),
                    "RunPlugin({0})".format(plugin.url_for("music_add_to_library", artist_name=artist_name,
                                                           track_name=track_name))
                )#,
#                (
#                    _("Musicvideo"),
#                    "RunPlugin({0})".format(plugin.url_for("music_play_video", artist_name=artist_name,
#                                                           track_name=track_name, mode='context'))
#                )
            ]
        else:
            path = plugin.url_for(music_play_video, artist_name=artist_name, track_name=track_name)
            icon = "DefaultMusicVideo.png"
            info_type = "musicvideos"
            context_menu = [
                (
                    _("Context musicvideo player"),
                    "PlayMedia({0})".format(plugin.url_for("music_play_video", artist_name=artist_name,
                                                           track_name=track_name, mode='context'))
                ),
                (
                    _("Add to library"),
                    "RunPlugin({0})".format(plugin.url_for("music_add_to_library", artist_name=artist_name,
                                                           track_name=track_name))
                ),
                (
                    _("Music"),
                    "RunPlugin({0})".format(plugin.url_for("music_play_audio", artist_name=artist_name,
                                                           track_name=track_name, mode='context'))
                )
            ]
        item = {
            'label': "{0} - {1}".format(artist_name, track_name),
            'path': path,
            'thumbnail': large_image,
            'icon': icon,
            'poster': large_image,
            'info': {
                'artist': artist_name,
            },
            'info_type': info_type,
            'context_menu': context_menu
        }
        items.append(item)
    return items


@plugin.route('/music/top_artists_by_country/<country>/<page>', options={'page': "1"})
def music_top_artists_by_country(country, page):
    results = lastfm.get_top_artists_by_country(country, page)
    artists = results["topartists"]["artist"]
    items = []
    for artist in artists:
        large_image = artist["image"][-1]["#text"]
        name = to_utf8(artist["name"])
        context_menu = [
            (
                _("Add to library"),
                "RunPlugin({0})".format(plugin.url_for("music_add_artist_to_library", artist_name=name))
            )
        ]
        item = {
            'label': name,
            'path': plugin.url_for(music_artist_albums, artist_name=name),
            'thumbnail': large_image,
            'icon': "DefaultMusic.png",
            'poster': large_image,
            'info': {
                'artist': name,
            },
            'info_type': 'music',
            'context_menu': context_menu
        }
        items.append(item)
    return items


@plugin.route('/music/top_tracks_by_country/<country>/<page>', options={'page': "1"})
def music_top_tracks_by_country(country, page):
    results = lastfm.get_top_tracks_by_country(country, page)
    tracks = results["tracks"]["track"]
    items = []
    for track in tracks:
        large_image = track["image"][-1]["#text"]
        track_name = to_utf8(track["name"])
        artist_name = to_utf8(track["artist"]["name"])
        context_menu = [
            (
                _("Context player"),
                "PlayMedia({0})".format(plugin.url_for("music_play_audio", artist_name=artist_name,
                                                       track_name=track_name, mode='context'))
            ),
            (
                _("Add to library"),
                "RunPlugin({0})".format(plugin.url_for("music_add_to_library", artist_name=artist_name,
                                                       track_name=track_name))
            )#,
#            (
#                _("Musicvideo"),
#                "RunPlugin({0})".format(plugin.url_for("music_play_video", artist_name=artist_name,
#                                                       track_name=track_name, mode='context'))
#            )
        ]
        item = {
            'label': "{0} - {1}".format(artist_name, track_name),
            'path': plugin.url_for(music_play_audio, artist_name=artist_name, track_name=track_name),
            'thumbnail': large_image,
            'icon': "DefaultMusic.png",
            'poster': large_image,
            'info': {
                'artist': artist_name,
            },
            'info_type': 'music',
            'context_menu': context_menu
        }

        items.append(item)
    return items


@plugin.route('/music/search_artist_term/<term>/<page>')
def music_search_artist_term(term, page):
    search_results = lastfm.search_artist(term, page)
    artists = search_results["artistmatches"]["artist"]
    items_per_page = search_results["opensearch:itemsPerPage"]
    start_index = search_results["opensearch:startIndex"]
    total_results = search_results["opensearch:totalResults"]
    items = []
    for artist in artists:
        large_image = artist["image"][-1]["#text"]
        name = to_utf8(artist["name"])
        context_menu = [
            (
                _("Add to library"),
                "RunPlugin({0})".format(plugin.url_for("music_add_artist_to_library", artist_name=name))
            )
        ]
        item = {
            'label': name,
            'path': plugin.url_for(music_artist_albums, artist_name=name),
            'thumbnail': large_image,
            'icon': "DefaultMusic.png",
            'poster': large_image,
            'info': {
                'artist': name,
            },
            'info_type': 'music',
            'context_menu': context_menu
        }

        items.append(item)
    if start_index + items_per_page < total_results:
        items.append({
            'label': _("Next >>"),
            'icon': get_icon_path("item_next"),
            'path': plugin.url_for(music_search_artist_term, term=term, page=int(page) + 1)
        })
    return items


@plugin.route('/music/search_album_term/<term>/<page>')
def music_search_album_term(term, page):
    search_results = lastfm.search_album(term, page)
    albums = search_results["albummatches"]["album"]
    items_per_page = search_results["opensearch:itemsPerPage"]
    start_index = search_results["opensearch:startIndex"]
    total_results = search_results["opensearch:totalResults"]
    items = []
    for album in albums:
        large_image = album["image"][-1]["#text"]
        album_name = to_utf8(album["name"])
        artist_name = to_utf8(album["artist"])
        context_menu = [
            (
                _("Add to library"),
                "RunPlugin({0})".format(plugin.url_for("music_add_album_to_library", artist_name=artist_name,
                                                       album_name=album_name))
            )
        ]
        item = {
            'label': "{0} - {1}".format(artist_name, album_name),
            'path': plugin.url_for(music_artist_album_tracks, artist_name=artist_name, album_name=album_name),
            'thumbnail': large_image,
            'icon': "DefaultMusic.png",
            'poster': large_image,
            'info': {
                'artist': artist_name,
            },
            'info_type': 'music',
            'context_menu': context_menu
        }

        items.append(item)
    if start_index + items_per_page < total_results:
        items.append({
            'label': _("Next >>"),
            'icon': get_icon_path("item_next"),
            'path': plugin.url_for(music_search_album_term, term=term, page=int(page) + 1)
        })
    return items


@plugin.route('/music/search_track_term/<term>/<page>')
def music_search_track_term(term, page):
    search_results = lastfm.search_track(term, page)
    tracks = search_results["trackmatches"]["track"]
    items_per_page = search_results["opensearch:itemsPerPage"]
    start_index = search_results["opensearch:startIndex"]
    total_results = search_results["opensearch:totalResults"]
    items = []
    for track in tracks:
        large_image = track["image"][-1]["#text"]
        track_name = to_utf8(track["name"])
        artist_name = to_utf8(track["artist"])
        context_menu = [
            (
                _("Context player"),
                "PlayMedia({0})".format(plugin.url_for("music_play_audio", artist_name=artist_name,
                                                       track_name=track_name, mode='context'))
            ),
            (
                _("Add to library"),
                "RunPlugin({0})".format(plugin.url_for("music_add_to_library", artist_name=artist_name,
                                                       track_name=track_name))
            ),
            (
                _("Musicvideo"),
                "RunPlugin({0})".format(plugin.url_for("music_play_video", artist_name=artist_name,
                                                       track_name=track_name, mode='context'))
            )
        ]
        item = {
            'label': "{0} - {1}".format(artist_name, track_name),
            'path': plugin.url_for(music_play_audio, artist_name=artist_name, track_name=track_name),
            'thumbnail': large_image,
            'icon': "DefaultMusic.png",
            'poster': large_image,
            'info': {
                'artist': artist_name,
            },
            'info_type': 'music',
            'context_menu': context_menu
        }

        items.append(item)
    if start_index + items_per_page < total_results:
        items.append({
            'label': _("Next >>"),
            'icon': get_icon_path("item_next"),
            'path': plugin.url_for(music_search_track_term, term=term, page=int(page) + 1)
        })
    return items


@plugin.route('/music/artist/<name>')
def music_artist(name):
    name = to_utf8(name)
    items = [
        {
            'label': _("Tracks"),
            'path': plugin.url_for("music_artist_tracks", artist_name=name),
            'icon': get_icon_path("music")
        },
        {
            'label': _("Albums"),
            'path': plugin.url_for("music_artist_albums", artist_name=name),
            'icon': get_icon_path("music")
        },
    ]
    return items


@plugin.route('/music/artist/<artist_name>/tracks/<page>', options={'page': "1"})
def music_artist_tracks(artist_name, page):
    artist_name = to_utf8(artist_name)
    results = lastfm.get_artist_top_tracks(artist_name, page)
    items = []
    for track in results["track"]:
        large_image = track["image"][-1]["#text"]
        track_name = to_utf8(track["name"])
        context_menu = [
            (
                _("Context player"),
                "PlayMedia({0})".format(plugin.url_for("music_play_audio", artist_name=artist_name,
                                                       track_name=track_name, mode='context'))
            ),
            (
                _("Add to library"),
                "RunPlugin({0})".format(plugin.url_for("music_add_to_library", artist_name=artist_name,
                                                       track_name=track_name))
            ),
            (
                _("Musicvideo"),
                "PlayMedia({0})".format(plugin.url_for("music_play_video", artist_name=artist_name,
                                                       track_name=track_name, mode='default'))
            )
        ]
        if plugin.get_setting(SETTING_PREFERRED_MUSIC_TYPE) == "audio":
            item = {
                'label': track_name,
                'path': plugin.url_for("music_play_audio", artist_name=artist_name, track_name=track_name),
                'thumbnail': large_image,
                'icon': "DefaultMusic.png",
                'poster': large_image,
                'info_type': 'music',
                'context_menu': context_menu,
            }
        else:
            item = {
                'label': track_name,
                'path': plugin.url_for("music_play_video", artist_name=artist_name, track_name=track_name),
                'thumbnail': large_image,
                'icon': "DefaultMusicVideo.png",
                'poster': large_image,
                'info_type': 'music',
                'context_menu': context_menu,
            }
        items.append(item)
    if results["@attr"]["totalPages"] > page:
        items.append({
            'label': _("Next >>"),
            'icon': get_icon_path("item_next"),
            'path': plugin.url_for(music_artist_tracks, artist_name=artist_name, page=int(page) + 1)
        })
    return items


@plugin.route('/music/artist/<artist_name>/albums/<page>', options={'page': "1"})
def music_artist_albums(artist_name, page):
    artist_name = to_utf8(artist_name)
    results = lastfm.get_artist_top_albums(artist_name, page)
    items = [
        {
            'label': _("All Tracks"),
            'path': plugin.url_for("music_artist_tracks", artist_name=artist_name),
            'icon': get_icon_path("music")
        }
    ]
    for album in results["album"]:
        album_name = to_utf8(album["name"])
        image = album['image'][-1]['#text']
        artist_album_name = to_utf8(album['artist']['name'])
        context_menu = [
            (
                _("Add to library"),
                "RunPlugin({0})".format(plugin.url_for("music_add_album_to_library", artist_name=artist_album_name,
                                                       album_name=album_name))
            )
        ]
        item = {
            'thumbnail': image,
            'label': "{0}".format(album_name),
            'info': {
                'title': album_name,
                'artist': [artist_album_name],
            },
            'info_type': 'music',
            'path': plugin.url_for("music_artist_album_tracks", artist_name=artist_name, album_name=album_name),
            'context_menu': context_menu
        }
        items.append(item)
    if results["@attr"]["totalPages"] > page:
        next_page = int(page) + 1
        items.append({
            'label': _("Next >>"),
            'icon': get_icon_path("item_next"),
            'path': plugin.url_for(music_artist_albums, artist_name=artist_name, page=next_page)
        })
    return items


@plugin.route('/music/artist/<artist_name>/album/<album_name>/tracks')
def music_artist_album_tracks(artist_name, album_name):
    artist_name = to_utf8(artist_name)
    album_name = to_utf8(album_name)
    results = lastfm.get_album_info(artist_name, album_name)
    items = []
    for track in results["tracks"]["track"]:
        track_name = to_utf8(track["name"])
        track_number = track["@attr"]["rank"]
        image = results["image"][-1]["#text"]
        context_menu = [
            (
                _("Context player"),
                "PlayMedia({0})".format(plugin.url_for("music_play_audio", artist_name=artist_name,
                                                       track_name=track_name, mode='context'))
            ),
            (
                _("Add to library"),
                "RunPlugin({0})".format(plugin.url_for("music_add_to_library", artist_name=artist_name,
                                                       track_name=track_name, album_name=album_name))
            ),
            (
                _("Musicvideo"),
                "RunPlugin({0})".format(plugin.url_for("music_play_video", artist_name=artist_name,
                                                       track_name=track_name, mode='default'))
            )
        ]
        if plugin.get_setting(SETTING_PREFERRED_MUSIC_TYPE) == "audio":
            item = {
                'label': "{0}. {1}".format(track_number, track_name),
                'path': plugin.url_for("music_play_audio", artist_name=artist_name, track_name=track_name),
                'thumbnail': image,
                'icon': "DefaultMusic.png",
                'poster': image,
                'info_type': 'music',
                'context_menu': context_menu,
            }
        else:
            item = {
                'label': "{0}. {1}".format(track_number, track_name),
                'path': plugin.url_for("music_play_video", artist_name=artist_name, album_name=album_name, track_name=track_name),
                'thumbnail': image,
                'icon': "DefaultMusicVideo.png",
                'poster': image,
                'info_type': 'music',
                'context_menu': context_menu,
            }
        items.append(item)
    return items


@plugin.route('/music/play/<artist_name>/<track_name>/<album_name>/<mode>', options={'album_name': "None",
                                                                                     'mode': 'default'})
def music_play(artist_name, track_name, album_name, mode):
    items = [
        {
            'label': _("Play Audio"),
            'path': plugin.url_for("music_play_audio", artist_name=artist_name, track_name=track_name,
                                   album_name=album_name, mode=mode)
        },
        {
            'label': _("Play Video"),
            'path': plugin.url_for("music_play_video", artist_name=artist_name, track_name=track_name,
                                   album_name=album_name, mode=mode)
        }
    ]
    if plugin.get_setting(SETTING_PREFERRED_MUSIC_TYPE) == "audio":
        music_play_audio(artist_name, track_name, album_name, mode)
    else:
        music_play_video(artist_name, track_name, album_name, mode)



@plugin.route('/music/play_audio/<artist_name>/<track_name>/<album_name>/<mode>', options={'album_name': "None",
                                                                                           'mode': 'default'})
def music_play_audio(artist_name, track_name, album_name, mode):
    if album_name == "None":
        track_info = lastfm.get_track_info(artist_name, track_name)
        if track_info and "album" in track_info:
            album_name = track_info["album"]["title"]
    play_music(artist_name, track_name, album_name, mode)


@plugin.route('/music/play_video/<artist_name>/<track_name>/<album_name>/<mode>', options={'album_name': "None",
                                                                                           'mode': 'default'})
def music_play_video(artist_name, track_name, album_name, mode):
    if album_name == "None":
        track_info = lastfm.get_track_info(artist_name, track_name)
        if track_info and "album" in track_info:
            album_name = track_info["album"]["title"]
    play_musicvideo(artist_name, track_name, album_name, mode)


@plugin.route('/music/add_to_library/<artist_name>/<track_name>/<album_name>', options={'album_name': "None"})
def music_add_to_library(artist_name, track_name, album_name):
    if album_name == "None":
        album_name = lastfm.get_track_info(artist_name, track_name)["album"]["title"]

    library_folder = setup_library(plugin.get_setting(SETTING_MUSIC_LIBRARY_FOLDER))

    add_music_to_library(library_folder, artist_name, album_name, track_name)
    scan_library(type="music")


@plugin.route('/music/add_album_to_library/<artist_name>/<album_name>')
def music_add_album_to_library(artist_name, album_name):
    library_folder = setup_library(plugin.get_setting(SETTING_MUSIC_LIBRARY_FOLDER))
    results = lastfm.get_album_info(artist_name, album_name)
    for track in results["tracks"]["track"]:
        track_name = to_utf8(track["name"])
        add_music_to_library(library_folder, artist_name, album_name, track_name)
    scan_library(type="music")


@plugin.route('/music/add_artist_to_library/<artist_name>')
def music_add_artist_to_library(artist_name):
    import math
    library_folder = setup_library(plugin.get_setting(SETTING_MUSIC_LIBRARY_FOLDER))
    album_results = lastfm.get_artist_top_albums(artist_name)
    total_albums = len(album_results)
    index = 0
    pDialog = xbmcgui.DialogProgress()
    pDialog.create(_('[COLOR ff0084ff]M[/COLOR]etalli[COLOR ff0084ff]Q[/COLOR]'), _("{0} {1} {2}").format(_("Adding"), artist_name, _("to library")))
    for album in album_results["album"]:
        album_name = to_utf8(album["name"])
        percent_done = int(math.floor((float(index) / total_albums) * 100))
        pDialog.update(percent_done, _("{0} {1} - {2} {3}").format(_("Adding"), artist_name,
                                                                   album_name, _("to library")))
        track_results = lastfm.get_album_info(artist_name, album_name)
        for track in track_results["tracks"]["track"]:
            if pDialog.iscanceled():
                pDialog.update(0)
                return
            track_name = to_utf8(track["name"])
            add_music_to_library(library_folder, artist_name, album_name, track_name)
        index += 1
        pDialog.update(0)
    scan_library(type="music")