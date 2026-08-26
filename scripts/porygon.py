#!.venv/bin/python

import argparse
import json

from reportworm_builder.builder import Builder
from reportworm_builder.builder_cache import BuilderCache

from ops.process_regional import process_regional, process_season, was_event_processed
from ops.config import Config
from ops.usage import compile_usage
from ops.home_bootstrap import get_home_bootstrap_data
from lib.util import get_season_bookends, make_nice_date_str
from lib.ruleset import load_rulesets

# every day I try to make this a little less crazy

def main():
    parser = argparse.ArgumentParser(
        prog="./scripts/porygon.py",
        description="Porygon is a simple script used for building regional/IC standings for Reportworm Standings. Please see README.md for more info.",
    )
    parser.add_argument('--mode', help="Build dev/prod/local version (dev default)")
    parser.add_argument('--build-only', action="store_true", help="Don't process any events, only rebuild pages")
    parser.add_argument('--process', help="Only process specified regional(s). Format: year1:name1,year2:name2")
    parser.add_argument('--grassroots', action="store_true", help="Process grassroots events as well")

    cl = parser.parse_args()

    allowlist = []
    if cl.process:
        chunks = cl.process.split(",")
        for chunk in chunks:
            year, code = chunk.split(':')
            allowlist.append(f"{year}-{code}")

    config = None
    try:
        with open("config.json") as file:
            config = Config(json.loads(file.read()))
    except FileNotFoundError:
        print("Couldn't load config, but that's okay")
        config = Config({})

    if cl.mode:
        config.mode = cl.mode

    manifest_file = "data/majors/manifest.json"

    manifest = {}
    try:
        with open(manifest_file) as file:
            manifest = json.loads(file.read())
    except FileNotFoundError:
        # manifest is required
        print("Could not find manifest, exiting")
        return

    builder_cache = BuilderCache("data/builder", config.mode == 'prod')

    if not cl.build_only:
        process_data(manifest, allowlist, builder_cache, config, cl.grassroots)

    build_site(config, builder_cache)

    print("All done!")


def process_data(
    manifest:dict,
    allowlist:list,
    builder_cache:BuilderCache,
    config:Config,
    grassroots:bool = False
):
    past_seasons = {}
    future_seasons = {}
    for season in list(filter(lambda s: s != manifest['current'], manifest['seasons'])):
        season_data = {
            "year": season,
            "dates": "",
            "events": 0,
            "champ": "",
            "champ_flag": "",
        }

        if season < manifest['current']:
            past_seasons[season] = season_data
        elif season > manifest['current']:
            future_seasons[season] = season_data

    rulesets = load_rulesets()

    process_seasons = manifest['seasons'][:]

    if grassroots:
        process_seasons = process_seasons + manifest['grassroots']

    current_majors = {}
    for year in process_seasons:
        majors = {}
        with open(f"data/majors/{year}.json", encoding='utf8') as file:
            data = json.loads(file.read())
            for item in data:
                majors[item['code']] = item
                if year == manifest['current']:
                    current_majors[item['code']] = item

            del data

        if year in past_seasons:
            first, _, worlds = get_season_bookends(majors)
            past_seasons[year]['dates'] = make_nice_date_str(first['start'], worlds['start'], use_full_months=True)

        if year in future_seasons:
            first, _, worlds = get_season_bookends(majors)
            future_seasons[year]['dates'] = make_nice_date_str(first['start'], worlds['start'], use_full_months=True)

        print(f"Building {year}")

        for event_code, event_info in majors.items():
            event_should_be_processed = len(allowlist) == 0 or f"{year}-{event_code}" in allowlist or f"{year}-*" in allowlist

            if not event_should_be_processed:
                print(f"[{year}] Checking for processed data for '{event_code}'... ", end="")
                _, proc_event_info = was_event_processed(year, event_code)
                majors[event_code].update(proc_event_info)
            else:
                print(f"[{year}] Processing data for '{event_code}'... ", end="")
                majors[event_code], data_type = process_regional(
                    year,
                    event_code,
                    event_info,
                    rulesets.get_ruleset(event_info['format']),
                    config.mode == 'prod',
                    grassroots
                )

            if year in past_seasons:
                past_seasons[year]['events'] += 1
            if year in future_seasons:
                future_seasons[year]['events'] += 1

            if event_code == "worlds" and 'winner' in majors[event_code] and year in past_seasons:
                past_seasons[year]['champ'] = majors[event_code]['winner']
                past_seasons[year]['champ_flag'] = majors[event_code]['winner_flag']

            if event_should_be_processed and majors[event_code]['processed']:
                print("building usage... ", end="")
                compile_usage(year, event_code, config.mode == 'prod', data_type)

            builder_cache.add_meta_ssi(
                f"{year}/{event_code}",
                f"{event_info['name']} Standings -- {year} Season -- Reportworm Standings",
                f"Reportworm Standings showcases standings and teamsheets for the {year} {event_info['name']}.",
            )

            print("Done!")

        print(f"[{year}] Processing season data... ", end="")
        process_season(year, majors)
        print("Done!")

        builder_cache.add_meta_ssi(
            f"{year}",
            f"{year} Season -- Reportworm Standings",
            f"Reportworm Standings showcases standings and teamsheets for the {year} VGC Season.",
        )

    # home (/) requires some bootstrap data
    past_seasons = list(past_seasons.values())
    past_seasons.reverse()

    future_seasons = list(future_seasons.values())
    # future_seasons will probably only ever have one year, so we don't need to sort it

    builder_cache.add_cache_data(
        'home_bootstrap',
        get_home_bootstrap_data(manifest['current'], current_majors, past_seasons, future_seasons)
    )

    builder_cache.save()


def build_site(config:Config, builder_cache:BuilderCache):
    builder = Builder(config.__dict__(), builder_cache.load())

    print("[ALL] Building site...", end="")
    builder.build()
    print("Done!")


if __name__ == "__main__":
    main()
