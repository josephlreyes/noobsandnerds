import abc
import xbmcaddon

abstractstaticmethod = abc.abstractmethod
class abstractclassmethod(classmethod):
    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)

class Scraper:
    __metaclass__ = abc.ABCMeta
    domains = ['localdomain']
    name = "Scraper"

    @classmethod
    def get_setting(cals, key):
        return xbmcaddon.Addon('script.module.nanscrapers').getSetting(key)

    @classmethod
    def _is_enabled(clas):
        return clas.get_setting(clas.name + '_enabled') == 'true'

    @classmethod
    def get_settings_xml(clas):
        xml = [
            '<setting id="%s_enabled" ''type="bool" label="Enabled" default="true"/>' % (clas.name)
        ]
        return xml

    def scrape_movie(self, title, year, imdb):
        pass

    def scrape_episode(self,title, show_year, year, season, episode, imdb, tvdb):
        pass

    def scrape_music(self, title, artist):
        pass
