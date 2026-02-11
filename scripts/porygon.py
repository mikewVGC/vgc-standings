
import argparse
import json
import subprocess

from ops.process_regional import process_regional, process_season, was_event_processed
from ops.site_builder import SiteBuilder
from ops.usage import Usage
from lib.util import get_season_bookends, make_nice_date_str

# every day I try to make this a little less crazy

def main():
    parser = argparse.ArgumentParser(
        prog="python3 porygon.py",
        description="Porygon is a simple script used for building regional/IC standings for Reportworm Standings. Please see README.md for more info.",
    )
    parser.add_argument('--prod', action="store_true", help="Build production version")
    parser.add_argument('--build-only', action="store_true", help="Don't process any events, only rebuild pages")
    parser.add_argument('--process', help="Only process specified regional(s). Format: year1:name1,year2:name2")

    cl = parser.parse_args()

    allowlist = []
    if cl.process:
        chunks = cl.process.split(",")
        for chunk in chunks:
            year, code = chunk.split(':')
            allowlist.append(f"{year}-{code}")

    config = {}
    try:
        with open("config.json") as file:
            config = json.loads(file.read())
    except FileNotFoundError:
        print("Couldn't load config, but that's okay")

    manifest = {}
    try:
        with open("data/majors/manifest.json") as file:
            manifest = json.loads(file.read())
    except FileNotFoundError:
        # manifest is required
        print("Could not find manifest.json, exiting")
        return

    non_current_seasons = {}
    for season in list(filter(lambda s: s != manifest['current'], manifest['seasons'])):
        non_current_seasons[season] = {
            "year": season,
            "dates": "",
        }

    usage = Usage(config)

    builder = SiteBuilder(config, cl.prod)

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
            first, _, worlds = get_season_bookends(majors)
            non_current_seasons[year]['dates'] = make_nice_date_str(first['start'], worlds['start'], use_full_months=True)

        print(f"Building {year}")

        for event_code, event_info in majors.items():
            event_should_be_processed = len(allowlist) == 0 or f"{year}-{event_code}" in allowlist or f"{year}-*" in allowlist

            if cl.build_only or not event_should_be_processed:
                print(f"[{year}] Checking for processed data for '{event_code}'... ", end="")
                _, proc_event_info = was_event_processed(year, event_code)
                majors[event_code].update(proc_event_info)
            else:
                print(f"[{year}] Processing data for '{event_code}'... ", end="")
                majors[event_code] = process_regional(year, event_code, event_info)

            if event_should_be_processed and majors[event_code]['processed']:
                print("building usage... ", end="")
                usage.compile_usage(year, event_code)

            builder.build_meta_ssi(
                f"{year}/{event_code}",
                f"{event_info['name']} Standings -- {year} Season -- Reportworm Standings",
                f"Reportworm Standings showcases standings and teamsheets for the {year} {event_info['name']}.",
            )

            print("Done!")

        print(f"[{year}] Processing season data... ", end="")
        process_season(year, majors)
        print("Done!")

        builder.build_meta_ssi(
            f"{year}",
            f"{year} Season -- Reportworm Standings",
            f"Reportworm Standings showcases standings and teamsheets for the {year} VGC Season.",
        )

    if cl.prod:
        print("[ALL] Minifying js and css... ", end="")
        subprocess.run(["go", "run", "scripts/packer/main.go"], capture_output=True)
        print("Done!")

    print("[ALL] Rebuilding season page... ", end="")
    builder.build_season()
    print("Done!")

    print("[ALL] Rebuilding tournament page... ", end="")
    builder.build_tournament()
    print("Done!")

    # the homepage does require a bunch of data, which I might change
    print("[ALL] Building home/index page...", end="")
    non_current_seasons = list(non_current_seasons.values())
    non_current_seasons.reverse()
    builder.build_home(manifest['current'], current_majors, non_current_seasons)
    print("Done!")

    print("All done!")

main()
