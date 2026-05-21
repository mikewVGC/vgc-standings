
import json
import shutil
import os

from datetime import date


class SiteBuilder():

    def __init__(self, config:dict = {}, prod:bool = False, cache:dict = {}) -> None:
        self.config = config
        self.prod = prod
        self.cache = cache

    def build_home(self) -> None:
        with open("site/templates/home.html", 'r') as homefile:
            home = homefile.read()

        home = self._add_header_footer(home)
        home = self._add_stylesheet(home)
        home = self._add_google_analytics(home)
        home = self._add_script('home', home)

        bootstrap = self.cache['home_bootstrap'] if 'home_bootstrap' in self.cache else {}

        home = home.replace('__BOOTSTRAP_DATA__', json.dumps(bootstrap))

        with open("public/index.html", 'w') as file:
            file.write(home)


    def build_season(self) -> None:
        with open("site/templates/season.html", 'r') as seasonfile:
            season = seasonfile.read()

        season = self._add_header_footer(season)
        season = self._add_stylesheet(season)
        season = self._add_google_analytics(season)
        season = self._add_script('season', season)

        with open("public/static/season.html", 'w') as file:
            file.write(season)


    def build_tournament(self) -> None:
        img_base = '/static/img/art'
        if self.prod and 'monImgBase' in self.config:
            img_base = self.config['monImgBase']

        with open("site/templates/tournament.html", 'r') as tourfile:
            tour = tourfile.read()

            with open("data/common/map-coords.json", 'r') as spritefile:
                spritedata = spritefile.read()
                tour = tour.replace('__SPRITE_COORDS_DATA__', spritedata)

            with open("data/common/hd-item-coords.json", 'r') as hditemfile:
                hditemdata = hditemfile.read()
                tour = tour.replace('__HD_ITEM_COORDS_DATA__', hditemdata)

            with open("data/common/country-codes.json", 'r') as countryfile:
                countrydata = countryfile.read()
                tour = tour.replace('__COUNTRY_CODE_DATA__', countrydata)

            if 'liveRefresh' in self.config:
                tour = tour.replace('__LIVE_UPDATE_FREQUENCY__', str(self.config['liveRefresh']))
            else:
                tour = tour.replace('__LIVE_UPDATE_FREQUENCY__', '""')

            tour = tour.replace('__MON_IMG_BASE__', img_base)

            tour = self._add_header_footer(tour)
            tour = self._add_stylesheet(tour)
            tour = self._add_google_analytics(tour)
            tour = self._add_script('tournament', tour)

        with open("public/static/tournament.html", 'w') as file:
            file.write(tour)


    def build_meta_ssi(self) -> None:
        if 'ssi' not in self.cache:
            return

        with open("site/templates/head-ssi.html", 'r') as headssifile:
            ssi_base = headssifile.read()

            for ssi_data in self.cache['ssi']:
                main_ssi = ssi_base.replace('__TITLE__', ssi_data['title'])
                main_ssi = main_ssi.replace('__DESCRIPTION__', ssi_data['description'])

                with open(f"public/static/ssi/{ssi_data['file']}.html", 'w') as file:
                    file.write(main_ssi)


    def _add_google_analytics(self, dest_data:str) -> str:
        tag = None
        if self.prod and 'googleTag' in self.config and len(self.config['googleTag']) > 0:
            tag = self.config['googleTag']

        ga = ''

        if tag:
            with open("site/templates/analytics.html", 'r') as gafile:
                ga = gafile.read()
                ga = ga.replace('__GOOGLE_TAG__', tag)

        dest_data = dest_data.replace('__GOOGLE_ANALYTICS__', ga)

        return dest_data


    def _add_header_footer(self, dest_data:str) -> str:
        with open("site/templates/header.html", 'r') as headerfile:
            header = headerfile.read()
            dest_data = dest_data.replace('__TEMPLATE_HEADER__', header)

        with open("site/templates/head.html", 'r') as headfile:
            head = headfile.read()
            dest_data = dest_data.replace('__TEMPLATE_HEAD__', head)

        with open("site/templates/footer.html", 'r') as footerfile:
            footer = footerfile.read()
            footer = footer.replace('__YEAR__', str(date.today().year))
            dest_data = dest_data.replace('__TEMPLATE_FOOTER__', footer)

        vue_tpl = "vue" if not self.prod else "vue-prod"
        with open(f"site/templates/{vue_tpl}.html", 'r') as vuefile:
            vue = vuefile.read()
            dest_data = dest_data.replace('__VUE__', vue)

        return dest_data


    def _add_script(self, script_name:str, dest_data:dict) -> str:
        min_script = '' if not self.prod else '.min'

        if not self.prod:
            shutil.copy(f"site/js/{script_name}.js", f"public/static/{script_name}.js")

        script_time = os.path.getmtime(f"site/js/{script_name}.js")
        dest_data = dest_data.replace('__SCRIPT_FILE__', f"/static/{script_name}{min_script}.js?{script_time}")

        return dest_data


    def _add_stylesheet(self, dest_data:str) -> str:
        min_style = '' if not self.prod else '.min'

        if not self.prod:
            shutil.copy("site/css/style.css", "public/static/style.css")

        style_time = os.path.getmtime("site/css/style.css")
        dest_data = dest_data.replace('__STYLESHEET_FILE__', f"/static/style{min_style}.css?{style_time}")

        return dest_data
