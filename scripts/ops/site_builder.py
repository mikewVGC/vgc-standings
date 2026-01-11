
import json
import os

from lib.util import make_season_info_str, make_nice_date_str


def build_home(year, majors, prod = False):
    with open("templates/home.html", 'r') as homefile:
        home = homefile.read()

    home = add_header_footer(home, prod)
    home = add_stylesheet(home, prod)
    home = add_script('home', home, prod)

    major_codes = list(majors.keys())
    first_major = majors[major_codes[0]]
    last_major = majors[major_codes[len(major_codes) - 2]]
    worlds = majors[major_codes[len(major_codes) - 1]]

    recent = list(filter(lambda major: major['processed'] == True, list(majors.values())))
    upcoming = list(filter(lambda major: major['processed'] == False, list(majors.values())))

    recent.reverse()

    bootstrap = {
        "currentSeason": year,
        "seasonStatus": make_season_info_str(majors),
        "seasonDates": make_nice_date_str(first_major['start'], last_major['start'], 'through', True),
        "worldsDate": worlds['dates'],
        "recent": recent[0:3],
        "upcoming": upcoming[0:3],
    }

    home = home.replace('__BOOTSTRAP_DATA__', json.dumps(bootstrap))

    with open(f"public/index.html", 'w') as file:
        file.write(home)


def build_season(year, prod = False):
    with open("templates/season.html", 'r') as seasonfile:
        season = seasonfile.read()

    season = add_header_footer(season, prod)
    season = add_stylesheet(season, prod)
    season = add_script('season', season, prod)

    with open(f"public/static/season.html", 'w') as file:
        file.write(season)


def build_tournament(prod = False, config = {}):
    img_base = '/static/img/art'
    if prod and 'monImgBase' in config:
        img_base = config['monImgBase']

    with open("templates/tournament.html", 'r') as tourfile:
        tour = tourfile.read()

        with open("data/common/map-coords.json", 'r') as spritefile:
            spritedata = spritefile.read()
            tour = tour.replace('__SPRITE_COORDS_DATA__', spritedata)

        tour = tour.replace('__MON_IMG_BASE__', img_base)

        tour = add_script('tournament', tour, prod)
        tour = add_header_footer(tour, prod)
        tour = add_stylesheet(tour, prod)

    with open(f"public/static/tournament.html", 'w') as file:
        file.write(tour)

    return True


def add_stylesheet(dest_data, prod = False):
    style_name = 'style' if not prod else 'style.min';

    style_time = os.path.getmtime(f"public/static/{style_name}.css")
    dest_data = dest_data.replace('__STYLESHEET_FILE__', f"/static/{style_name}.css?{style_time}")

    return dest_data


def add_script(script_name, dest_data, prod = False):
    if prod:
        script_name = f"{script_name}.min"

    script_time = os.path.getmtime(f"public/static/{script_name}.js")
    dest_data = dest_data.replace('__SCRIPT_FILE__', f"/static/{script_name}.js?{script_time}")

    return dest_data


def add_header_footer(dest_data, prod = False):
    with open("templates/header.html", 'r') as headerfile:
        header = headerfile.read()
        dest_data = dest_data.replace('__TEMPLATE_HEADER__', header)

    with open("templates/head.html", 'r') as headfile:
        head = headfile.read()
        dest_data = dest_data.replace('__TEMPLATE_HEAD__', head)

    with open("templates/footer.html", 'r') as footerfile:
        footer = footerfile.read()
        dest_data = dest_data.replace('__TEMPLATE_FOOTER__', footer)

    vue_tpl = "vue" if not prod else "vue-prod"
    with open(f"templates/{vue_tpl}.html", 'r') as vuefile:
        vue = vuefile.read()
        dest_data = dest_data.replace('__VUE__', vue)

    return dest_data
