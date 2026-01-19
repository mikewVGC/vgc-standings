
import json

from lib.tournament import (
    get_tournament_structure,
    player_earned_points,
    player_made_phase_two,
    player_made_cut,
)

# I don't think this needs to be a class

class Usage:

    def __init__(self, config):
        self.config = config

    def compile_usage(self, year, event_code):
        data = {}
        try:
            with open(f"public/data/{year}/{event_code}.json", 'r') as file:
                data = json.loads(file.read())
        except FileNotFoundError:
            print(f"usage could not read public/data/{year}/{event_code}.json", end="")
            return

        standings = data['standings']

        tour_format = get_tournament_structure(year, len(standings.keys()))

        mon_stats = {}
        item_stats = {}

        for player, pdata in standings.items():
            for mon in pdata['team']:
                code = mon['code']
                if code not in mon_stats:
                    mon_stats[code] = {
                        "name": mon['name'],
                        "code": code,
                        "counts": {
                            "total": 0,
                            "points": 0,
                            "phase2": 0,
                            "cut": 0,
                        },
                        "w": 0,
                        "l": 0,
                        #"moves": {},
                        #"items": {},
                        #"abilities": {},
                        #"teammates": {},
                    }

                mon_stats[code]['counts']['total'] += 1

                mon_stats[code]['w'] += pdata['record']['w']
                mon_stats[code]['l'] += pdata['record']['l']

                if player_earned_points(pdata, tour_format):
                    mon_stats[code]['counts']['points'] += 1

                if player_made_phase_two(pdata, tour_format):
                    mon_stats[code]['counts']['phase2'] += 1

                if player_made_cut(pdata, tour_format):
                    mon_stats[code]['counts']['cut'] += 1

        mon_stats = list(mon_stats.values())

        mon_stats.sort(key=lambda mon: mon['counts']['total'], reverse=True)

        with open(f"public/data/{year}/{event_code}-usage.json", 'w') as file:
            file.write(json.dumps(mon_stats))


