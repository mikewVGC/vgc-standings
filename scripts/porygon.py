
import argparse
import json
import subprocess

from ops.process_regional import process_regional, process_season
from ops.site_builder import build_home, build_season, build_tournament

def main():
    parser = argparse.ArgumentParser(
        prog="python3 porygon.py",
        description="Porygon is a simple script used for building regional/IC standings for Reportworm Standings. Please see README.md for more info.",
    )
    parser.add_argument('year', type=int, help="The season/year you want to process")
    parser.add_argument('--prod', action="store_true", help="Build production version")

    cl = parser.parse_args()

    config = {}
    try:
        with open(f"config.json") as file:
            config = json.loads(file.read())
    except FileNotFoundError:
        ...

    majors = {}
    with open(f"data/majors/{cl.year}.json", encoding='utf8') as file:
        data = json.loads(file.read())
        for item in data:
            majors[item['code']] = item

        del data

    for event_code, event_info in majors.items():        
        print(f"Processing data for '{event_code}'... ", end="")
        majors[event_code]['processed'] = process_regional(cl.year, event_code, event_info)
        print("Done!")

    if cl.prod:
        print("Minifying js and css... ", end="")
        subprocess.run(["go", "run", "scripts/packer/main.go"], capture_output=True)
        print("Done!")

    print("Rebuilding tournament page... ", end="")
    build_tournament(cl.prod, config)
    print("Done!")

    print("Processing season data and building season page... ", end="")
    process_season(cl.year, majors)
    build_season(cl.year, cl.prod)
    print("Done!")

    print("Building home/index page...", end="")
    build_home(cl.year, majors, cl.prod)
    print("Done!")

    print("All done!")

main()
