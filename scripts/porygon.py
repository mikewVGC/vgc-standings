
import argparse
import json
import subprocess

from ops.process_regional import process_regional, process_season
from ops.site_builder import SiteBuilder
from lib.util import get_season_bookends, make_nice_date_str


def main():
    parser = argparse.ArgumentParser(
        prog="python3 porygon.py",
        description="Porygon is a simple script used for building regional/IC standings for Reportworm Standings. Please see README.md for more info.",
    )
    parser.add_argument('--prod', action="store_true", help="Build production version")
    parser.add_argument('--seasons', help="Comma separated list of years to rebuild (otherwise all will be built)")

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

    builder = SiteBuilder(config, cl.prod)

    seasons_to_build = [] if not cl.seasons else cl.seasons.split(',')

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

        if len(seasons_to_build) and str(year) not in seasons_to_build:
            print(f"Skipping build for {year}")
            continue

        print(f"Building {year}")

        for event_code, event_info in majors.items():
            print(f"[{year}] Processing data for '{event_code}'... ", end="")
            majors[event_code]['processed'] = process_regional(year, event_code, event_info)
            print("Done!")

        if cl.prod:
            print(f"[{year}] Minifying js and css... ", end="")
            subprocess.run(["go", "run", "scripts/packer/main.go"], capture_output=True)
            print("Done!")

        print(f"[{year}] Processing season data and building season page... ", end="")
        process_season(year, majors)
        builder.build_season(year)
        print("Done!")

    print(f"[ALL] Rebuilding tournament page... ", end="")
    builder.build_tournament()
    print("Done!")

    print(f"[{year}] Building home/index page...", end="")
    builder.build_home(manifest['current'], current_majors, list(non_current_seasons.values()))
    print("Done!")

    print("All done!")

main()
