import time

import xbmc
from BeautifulSoup import BeautifulSoup

from resources.lib.modules import proxy


def get_acesoplisting():
    xml = "<fanart>https://www.dropbox.com/s/x3zg9ovot6vipjh/smoke_men-wallpaper-1920x1080.jpg?raw=true</fanart>\n\n\n" \
          "<item>\n" \
          "\t<title>[COLORred]Will require Plexus addon to watch Acestream links.[/COLOR]</title>\n" \
          "\t<link> </link>\n" \
          "\t<thumbnail> </thumbnail>\n" \
          "</item>\n\n" \
          "<item>\n" \
          "\t<title>[COLORred]Download in Community Portal.[/COLOR]</title>\n" \
          "\t<link> </link>\n" \
          "\t<thumbnail> </thumbnail>\n" \
          "</item>\n\n" \
          "<item>\n" \
          "\t<title>[COLORpurple]############## [COLORcyan]Live Sporting Events[COLORpurple] ##############[/COLOR]</title>\n" \
          "\t<link> </link>\n" \
          "\t<thumbnail> </thumbnail>\n" \
          "</item>\n"

    try:
        html = proxy.get2("http://www.acesoplisting.in/", 'class="listing"')
        scraped_html = BeautifulSoup(html)
        table = scraped_html.findAll("table", attrs={'class': 'listing'})[-1]

        rows = table.findAll("tr")
        date = None
        is_today = False
        day_xml = ""
        found_links = False
        for row in rows:
            cells = row.findAll("td")
            if len(cells) < 5:
                date = cells[0].text.strip()
                today_number = time.gmtime().tm_mday
                if str(today_number) in date:
                    is_today = True
                if is_today:
                    day_xml = "\n" \
                              "<item>\n" \
                              "\t<title>%s</title>\n" \
                              "\t<link></link>\n" \
                              "\t<thumbnail></thumbnail>\n" \
                              "</item>\n" % (date)
            elif is_today:
                event_time = cells[0].text.strip()
                split_time = event_time.split(":")
                event_hours = int(split_time[0])
                event_minutes = split_time[1]
                est_event_hours = event_hours - 4

                if est_event_hours >= 4:
                    xml += day_xml
                    day_xml = ""
                if est_event_hours < 0:
                    est_event_hours = 24 - abs(est_event_hours)
                if est_event_hours >= 12:
                    if not est_event_hours == 12:
                        est_event_hours = est_event_hours - 12
                    suffix = "PM"
                else:
                    suffix = "AM"
                event_time = "%s:%s %s" % (est_event_hours, event_minutes, suffix)

                sport = cells[1].text.strip()
                match = cells[2].text.replace("\n", "").strip()
                match = " ".join(match.split())
                league = cells[3].text.strip()
                if league == "USA NFL":
                    thumbnail = "http://organizationalphysics.com/wp-content/uploads/2013/12/NFLShield.png"
                elif league == "WWE":
                    thumbnail = "http://i.imgur.com/UsYsZ.png"
                elif league == "USA NBA":
                    thumbnail = "https://lh3.googleusercontent.com/gfS15xuST6IP3e-ZDy63XLNl-ZxxTqo-NxXuIy5dKWQIjX_8s_T0Sz1mgTc0-78juBc=w170"
                elif league == "PREMIER LEAGUE":
                    thumbnail = "https://d1fy1ym40biffm.cloudfront.net/images/logos/leagues/f633765f43fafaf2120a1bb9b2a7babd4f0d9380ed1bc72925c29ba18ace9269.png"
                elif sport == "SOCCER":
                    thumbnail = "http://themes.zozothemes.com/mist/sports/wp-content/uploads/sites/6/2015/10/soccer-player.png"
                elif sport == "MOTOGP":
                    thumbnail = "https://www.bestvpnprovider.com/wp-content/uploads/2015/05/MotoGp_Logo.jpg"
                elif sport == "FORMULA 1":
                    thumbnail = "http://d3t1wwu6jp9wzs.cloudfront.net/wp-content/uploads/2016/05/photo.jpg"
                elif sport == "UFC":
                    thumbnail = "http://img3.wikia.nocookie.net/__cb20130511014401/mixedmartialarts/images/c/c5/UFC_logo.png"
                else:
                    thumbnail = ""

                links = cells[4].findAll("a")

                if len(links) != 0:
                    found_links = True
                for link in links:
                    href = link["href"]
                    if "acestream://" in href:
                        xml += "\n" \
                               "<item>\n" \
                               "\t<title>[COLORlime]%s -[COLORorange]  %s[COLORred]  Acestreams[COLORwhite] %s EST[/COLOR]</title>\n" \
                               "\t<link>plugin://program.plexus/?mode=1&url=%s&name=TA+Sports</link>\n" \
                               "\t<thumbnail>%s</thumbnail>\n" \
                               "</item>\n" % (sport, match, event_time, href, thumbnail)
                    elif "sop://" in href:
                        xml += "\n" \
                               "<item>\n" \
                               "\t<title>[COLORlime]%s -[COLORorange]  %s[COLORblue]  Sopcast[COLORwhite] %s EST[/COLOR]</title>\n" \
                               "\t<link>plugin://program.plexus/?url=%s&mode=2&name=TASPORTS</link>\n" \
                               "\t<thumbnail>%s</thumbnail>\n" \
                               "</item>\n" % (sport, match, event_time, href, thumbnail)
        if not found_links:
            xml = "<fanart>https://www.dropbox.com/s/x3zg9ovot6vipjh/smoke_men-wallpaper-1920x1080.jpg?raw=true</fanart>\n\n\n" \
                  "<item>\n" \
                  "\t<title>[COLORred]Will require Plexus addon to watch Acestream links.[/COLOR]</title>\n" \
                  "\t<link> </link>\n" \
                  "\t<thumbnail> </thumbnail>\n" \
                  "</item>\n\n" \
                  "<item>\n" \
                  "\t<title>[COLORred]Download in Community Portal.[/COLOR]</title>\n" \
                  "\t<link> </link>\n" \
                  "\t<thumbnail> </thumbnail>\n" \
                  "</item>\n\n" \
                  "<item>\n" \
                  "\t<title>[COLORpurple]############## [COLORcyan]Live Sporting Events[COLORpurple] ##############[/COLOR]</title>\n" \
                  "\t<link> </link>\n" \
                  "\t<thumbnail> </thumbnail>\n" \
                  "</item>\n" \
                  "\n" \
                   "<item>\n" \
                   "\t<title>Currently No Games Available</title>\n" \
                   "\t<link></link>\n" \
                   "\t<thumbnail></thumbnail>\n" \
                   "</item>\n"
        return xml
    except:
        pass
