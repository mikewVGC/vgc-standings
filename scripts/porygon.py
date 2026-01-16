
import argparse
import json
import subprocess

from ops.process_regional import process_regional, process_season, was_event_processed
from ops.site_builder import SiteBuilder
from ops.cache_data import CacheData
from lib.util import get_season_bookends, make_nice_date_str

# every day I try to make this a little less crazy

def main():
    parser = argparse.ArgumentParser(
        prog="python3 porygon.py",
        description="Porygon is a simple script used for building regional/IC standings for Reportworm Standings. Please see README.md for more info.",
    )
    parser.add_argument('--prod', action="store_true", help="Build production version")
    parser.add_argument('--build-only', action="store_true", help="Don't process any events, only rebuild pages")

    cl = parser.parse_args()

    config = {}
    try:
        with open(f"config.json") as file:
            config = json.loads(file.read())
    except FileNotFoundError:
        print("Couldn't load config, but that's okay")

    manifest = {}
    try:
        with open(f"data/majors/manifest.json") as file:
            manifest = json.loads(file.read())
    except FileNotFoundError:
        # manifest is required
        print("Could not find manifest.json, exiting")
        return

    cache = None
    if 'cacheJson' in config and config['cacheJson']:
        cache = CacheData()
        print(cache.keys())

    builder = SiteBuilder(config, cl.prod)

    non_current_seasons = {}
    for season in list(filter(lambda s: s != manifest['current'], manifest['seasons'])):
        non_current_seasons[season] = {
            "year": season,
            "dates": "",
        }

    current_majors = {}
    for year in manifest['seasons']:
        majors = {}
        with open(f"data/majors/{year}.json", encoding='utf8') as file:
            data = json.loads(file.read())
            for item in data:
                majors[item['code']] = item
                if year == manifest['current']:
                    current_majors[item['code']] = item

            del data

        if year in non_current_seasons:
            f, l, w = get_season_bookends(majors)
            non_current_seasons[year]['dates'] = make_nice_date_str(f['start'], w['start'], use_full_months=True)

        print(f"Building {year}")

        for event_code, event_info in majors.items():
            if cl.build_only:
                print(f"[{year}] Checking for processed data for '{event_code}'... ", end="")
                majors[event_code]['processed'] = was_event_processed(year, event_code)
            else:
                print(f"[{year}] Processing data for '{event_code}'... ", end="")
                majors[event_code]['processed'] = process_regional(year, event_code, event_info)

            if cache and cache.cache_event(year, event_code):
                print(f"[Wrote to cache] ", end="")

            print("Done!")

        print(f"[{year}] Processing season data... ", end="")
        process_season(year, majors)
        print("Done!")

        if cache and cache.cache_season(year):
            print(f"[{year}] Successfully cached {year}")

    if cl.prod:
        print(f"[ALL] Minifying js and css... ", end="")
        subprocess.run(["go", "run", "scripts/packer/main.go"], capture_output=True)
        print("Done!")

    print(f"[ALL] Rebuilding season page... ", end="")
    builder.build_season()
    print("Done!")

    print(f"[ALL] Rebuilding tournament page... ", end="")
    builder.build_tournament()
    print("Done!")

    # the homepage does require a bunch of data, which I might change
    print(f"[ALL] Building home/index page...", end="")
    builder.build_home(manifest['current'], current_majors, list(non_current_seasons.values()))
    print("Done!")

    print("All done!")

main()
