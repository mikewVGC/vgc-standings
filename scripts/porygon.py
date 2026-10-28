#!.venv/bin/python

import argparse
import json

from lib.keymap import KeyMap
from lib.ruleset import load_rulesets
from lib.scanner import DataScanner
from lib.util import get_season_bookends, make_nice_date_str
from ops.config import Config
from ops.home_bootstrap import get_home_bootstrap_data
from ops.process_regional import (
    process_regional,
    process_season,
    was_event_processed,
    write_regional,
)
from ops.usage import compile_usage, write_usage
from reportworm_builder.builder import Builder
from reportworm_builder.builder_cache import BuilderCache

# every day I try to make this a little less crazy

def main():
    parser = argparse.ArgumentParser(
        prog="./scripts/porygon.py",
        description="Porygon is a simple script used for building regional/IC standings for Reportworm Standings. Please see README.md for more info.",
    )
    parser.add_argument('--mode', help="Build dev/prod/local version (dev default)")
    parser.add_argument('--build-only', action="store_true", help="Don't process any events, only rebuild pages")
    parser.add_argument('--process', help="Only process specified regional(s). Format: year1:name1,year2:name2. Wildcard is allowed for names (2025:*)")
    parser.add_argument('--grassroots', action="store_true", help="Process grassroots events as well")
    parser.add_argument('--missing-team-scan', action="store_true", help="Run a scan for missing teams. No other processing.")
    parser.add_argument('--build-nginx-map', action="store_true", help="Build the mappings file for nginx (requires nginx reload)")

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

    if cl.missing_team_scan:
        print("Team scan selected, running now...")
        scanner = DataScanner(manifest)
        scanner.scan()
        print("Done! Exiting.")
        return

    builder_cache = BuilderCache("data/builder", config.mode == 'prod')

    if not cl.build_only:
        process_data(manifest, allowlist, builder_cache, config, cl.grassroots)

    # build nginx mappings file (doesn't need to happen every time)
    if cl.build_nginx_map:
        build_nginx_map(manifest['seasons'] + manifest['grassroots'])

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

            players = {}

            if not event_should_be_processed:
                print(f"[{year}] Checking for processed data for '{event_code}'... ", end="")
                _, proc_event_info = was_event_processed(year, event_code)
                event_info.update(proc_event_info)
            else:
                print(f"[{year}] Processing data for '{event_code}'... ", end="")
                majors[event_code], players, data_type = process_regional(
                    year,
                    event_code,
                    event_info,
                    rulesets.get_ruleset(event_info['format']),
                    config.mode == 'prod',
                    grassroots
                )

                if event_info['status'] != 'upcoming':
                    write_regional(
                        f"{year}/{event_code}",
                        event_info,
                        players,
                        config.mode == 'prod'
                    )

            if year in past_seasons:
                past_seasons[year]['events'] += 1
            if year in future_seasons:
                future_seasons[year]['events'] += 1

            if event_code == "worlds" and 'winner' in event_info and year in past_seasons:
                past_seasons[year]['champ'] = event_info['winner']
                past_seasons[year]['champ_flag'] = event_info['winner_flag']

            if event_should_be_processed and event_info['processed']:
                print("building usage... ", end="")
                mon_stats = compile_usage(year, event_info, players, config.mode == 'prod', data_type)

                write_usage(f"{year}/{event_code}", mon_stats, config.mode == 'prod')

            print("Done!")

        print(f"[{year}] Processing season data... ", end="")
        process_season(year, majors, config.mode == "prod")
        print("Done!")

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


"""
simple call to Builder
"""
def build_site(config:Config, builder_cache:BuilderCache):
    builder = Builder(config.__dict__(), builder_cache.load())

    print("[ALL] Building site...", end="")
    builder.build()
    print("Done!")


"""
build the nginx map separate (this will read all compiled files)
"""
def build_nginx_map(process_seasons):
    key_map = KeyMap()

    for year in process_seasons:
        events = []
        with open(f"public/data/{year}.json", encoding='utf8') as sfile:
            events = json.loads(sfile.read())
        for event in events:
            key_map.add_mapping(f"event/{event['code']}", event['name'])

            event_data = {}
            try:
                with open(f"public/data/{year}/{event['code']}.json", encoding='utf8') as efile:
                    event_data = json.loads(efile.read())
            except FileNotFoundError:
                continue

            for player in event_data['standings'].values():
                key_map.add_mapping(f"player/{player['code']}", player['name'])

            usage = []
            try:
                with open(f"public/data/{year}/{event['code']}-usage.json", encoding='utf8') as ufile:
                    usage = json.loads(ufile.read())
            except FileNotFoundError:
                continue

            for mon in usage:
                key_map.add_mapping(f"mon/{mon['code']}", mon['name'])

    # final keymap stuff
    key_map.add_mapping('mon', "usage information and conversion rates")
    key_map.add_mapping('player', "teamsheet and opponents")
    key_map.dump()

if __name__ == "__main__":
    main()
