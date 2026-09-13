
# brain-square-quarter

import json

class DataScanner:

    def __init__(self, manifest:dict):
        self.manifest = manifest

        config = {}
        try:
            with open("scanner.json") as file:
                config = json.loads(file.read())
        except FileNotFoundError:
            ...

        self.ignore_list = config['ignore'] if 'ignore' in config else []


    def scan(self):
        for year in self.manifest['seasons']:
            season = []
            try:
                with open(f"public/data/{year}.json") as file:
                    season = json.loads(file.read())
            except FileNotFoundError:
                print(f"[scanner] Couldn't open {year}.json, skipping")
                continue

            self.scan_season(season, year)


    def scan_season(self, season_data:list, year:int):
        for event_info in season_data:
            event = {}

            if f"{year}/{event_info['code']}" in self.ignore_list:
                continue

            try:
                with open(f"public/data/{year}/{event_info['code']}.json") as file:
                    event = json.loads(file.read())
            except FileNotFoundError:
                continue

            self.scan_players(event['standings'], f"{year}/{event_info['code']}")


    def scan_players(self, standings_data:dict, event_code:str):
        for player in standings_data.values():
            if len(player['team']) == 0:
                print(f"[scanner][{event_code}] MISSING TEAM! Team for {player['name']} ({player['code']}) is empty.")
