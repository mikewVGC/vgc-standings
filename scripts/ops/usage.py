
import json

from lib.tournament import (
    get_tournament_structure,
    player_earned_points,
    player_made_phase_two,
    player_made_cut,
    get_points_threshold,
)
from lib.formes import get_mon_data_from_code, get_mon_alt_from_code
from lib.util import make_item_code


def compile_usage(year:int, event_code:str) -> None:
    data = {}
    try:
        with open(f"public/data/{year}/{event_code}.json", 'r') as file:
            data = json.loads(file.read())
    except FileNotFoundError:
        print(f"usage could not read public/data/{year}/{event_code}.json", end="")
        return

    standings = data['standings']

    num_players = len(standings.keys())

    tour_format = get_tournament_structure(year, num_players, data['event'])

    mon_stats = {}
    # item_stats = {}

    for player, pdata in standings.items():
        for mon in pdata['team']:
            code = mon['code']
            if code not in mon_stats:
                dexNum, ptype = get_mon_data_from_code(code)
                alt = get_mon_alt_from_code(code)
                if alt:
                    dexNum = alt

                mon_stats[code] = {
                    "name": mon['name'],
                    "code": code,
                    "dex": dexNum,
                    "counts": {
                        "total": 0,
                        "points": 0,
                        "phase2": 0,
                        "cut": 0,
                    },
                    "w": 0,
                    "l": 0,
                    "players": [],
                    "items": {},
                    "abilities": {},
                    "teras": {},
                    "moves": {},
                }

            item_name = mon['item'] if mon['item'] else "No Item"
            item_code = make_item_code(item_name)
            if item_code not in mon_stats[code]['items']:
                mon_stats[code]['items'][item_code] = {
                    'name': item_name,
                    'code': item_code,
                    'count': 0,
                }
            mon_stats[code]['items'][item_code]['count'] += 1

            ability = mon['ability'] if mon['ability'] else "Unknown"
            if ability not in mon_stats[code]['abilities']:
                mon_stats[code]['abilities'][ability] = {
                    'name': ability,
                    'count': 0,
                }
            mon_stats[code]['abilities'][ability]['count'] += 1

            tera = mon['tera'] if mon['tera'] else "Unknown"
            if tera not in mon_stats[code]['teras']:
                mon_stats[code]['teras'][tera] = {
                    'name': tera,
                    'count': 0,
                }
            mon_stats[code]['teras'][tera]['count'] += 1

            for move_name in mon['moves']:
                if move_name not in mon_stats[code]['moves']:
                    mon_stats[code]['moves'][move_name] = {
                        'name': move_name,
                        'count': 0,
                    }
                mon_stats[code]['moves'][move_name]['count'] += 1

            mon_stats[code]['players'].append(player)

            mon_stats[code]['counts']['total'] += 1

            mon_stats[code]['w'] += pdata['record']['w']
            mon_stats[code]['l'] += pdata['record']['l']

            if player_earned_points(pdata, get_points_threshold(year, num_players)):
                mon_stats[code]['counts']['points'] += 1

            if player_made_phase_two(pdata, tour_format):
                mon_stats[code]['counts']['phase2'] += 1

            if player_made_cut(pdata, tour_format):
                mon_stats[code]['counts']['cut'] += 1

    mon_stats = list(mon_stats.values())

    mon_stats.sort(key=lambda mon: mon['counts']['total'], reverse=True)

    for mon_stat in mon_stats:
        mon_stat['items'] = list(mon_stat['items'].values())
        mon_stat['items'].sort(key=lambda item: item['count'], reverse=True)

        mon_stat['abilities'] = list(mon_stat['abilities'].values())
        mon_stat['abilities'].sort(key=lambda ability: ability['count'], reverse=True)

        mon_stat['teras'] = list(mon_stat['teras'].values())
        mon_stat['teras'].sort(key=lambda tera: tera['count'], reverse=True)

        mon_stat['moves'] = list(mon_stat['moves'].values())
        mon_stat['moves'].sort(key=lambda move: move['count'], reverse=True)

    with open(f"public/data/{year}/{event_code}-usage.json", 'w') as file:
        file.write(json.dumps(mon_stats))
