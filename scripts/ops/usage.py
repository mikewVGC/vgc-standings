
import json

from lib.tournament import (
    get_tournament_structure,
    player_earned_points,
    player_made_phase_two,
    player_made_cut,
    get_points_threshold,
)
from lib.formes import (
    get_mon_data_from_code,
    get_mon_alt_from_code,
    get_mega_form,
)
from lib.util import make_item_code


def compile_usage(year:int, event_code:str, prod:bool, limitless:bool = False) -> None:
    data = {}
    try:
        with open(f"public/data/{year}/{event_code}.json", 'r') as file:
            data = json.loads(file.read())
    except FileNotFoundError:
        print(f"usage could not read public/data/{year}/{event_code}.json", end="")
        return

    standings = data['standings']
    event_info = data['event']

    num_players = len(standings.keys())

    tour_format = get_tournament_structure(year, num_players, data['event'])

    mon_stats = {}
    # item_stats = {}

    mon_hashes = {}

    for player, pdata in standings.items():

        earned_points = player_earned_points(pdata, get_points_threshold(year, num_players))
        made_phase_two = player_made_phase_two(pdata, tour_format)
        made_cut = player_made_cut(pdata, tour_format)

        for mon in pdata['team']:
            code = mon['code']

            mega_form = ""
            if event_info['rules']['mega']:
                mega_form = get_mega_form(code, mon)

            if code not in mon_stats:
                dex_num, ptype, _ = get_mon_data_from_code(code)
                alt = get_mon_alt_from_code(code)
                if alt:
                    dex_num = alt

                mon_stats[code] = {
                    "name": mon['name'].title(),
                    "code": code,
                    "dex": dex_num,
                    "counts": {
                        "total": 0,
                        "points": 0,
                        "phase2": 0,
                        "cut": 0,
                    },
                    "w": 0,
                    "l": 0,
                    "points": 0,
                    "distinct": 0,
                    "players": [],
                    "items": {},
                    "abilities": {},
                    "teras": {},
                    "natures": {},
                    "moves": {},
                    "teammates": {},
                    "forms": {},
                }

            if len(mega_form) and mega_form not in mon_stats[code]['forms']:
                _, _, form_name = get_mon_data_from_code(mega_form)
                mon_stats[code]['forms'][mega_form] = {
                    "name": form_name,
                    "code": mega_form,
                    "counts": {
                        "total": 0,
                        "points": 0,
                        "phase2": 0,
                        "cut": 0,
                    }
                }

            if code not in mon_hashes:
                mon_hashes[code] = {}

            moves = sorted(mon['moves'])
            mon_hash = f"{mon['code']}-{mon['ability']}-{mon['item']}-{mon['tera']}" + '-'.join(moves)

            if mon_hash not in mon_hashes[code]:
                mon_hashes[code][mon_hash] = 0

            mon_hashes[code][mon_hash] += 1

            if event_info['status'] == "complete" and 'points' in pdata:
                mon_stats[code]['points'] += pdata['points']

            item_name = mon['item'] if mon['item'] else "No Item"
            item_code = make_item_code(item_name)
            update_mon_stats(
                mon_stats[code],
                item_code,
                item_name,
                'items',
                earned_points,
                made_phase_two,
                made_cut
            )

            ability = mon['ability'] if mon['ability'] else "Unknown"
            update_mon_stats(
                mon_stats[code],
                ability,
                ability,
                'abilities',
                earned_points,
                made_phase_two,
                made_cut
            )

            tera = mon['tera'] if mon['tera'] else ""
            if len(tera):
                update_mon_stats(
                    mon_stats[code],
                    tera,
                    tera,
                    'teras',
                    earned_points,
                    made_phase_two,
                    made_cut
                )

            nature = mon['nature'] if mon['nature'] else ""
            if len(nature):
                update_mon_stats(
                    mon_stats[code],
                    nature,
                    nature,
                    'natures',
                    earned_points,
                    made_phase_two,
                    made_cut
                )

            for move_name in mon['moves']:
                update_mon_stats(
                    mon_stats[code],
                    move_name,
                    move_name,
                    'moves',
                    earned_points,
                    made_phase_two,
                    made_cut
                )

            for tmate in pdata['team']:
                mate_code = tmate['code']
                if mate_code == code:
                    continue

                update_mon_stats(
                    mon_stats[code],
                    mate_code,
                    tmate['name'],
                    'teammates',
                    earned_points,
                    made_phase_two,
                    made_cut
                )

            mon_stats[code]['players'].append(player)

            mon_stats[code]['counts']['total'] += 1
            if len(mega_form):
                mon_stats[code]['forms'][mega_form]['counts']['total'] += 1

            mon_stats[code]['w'] += pdata['record']['w']
            mon_stats[code]['l'] += pdata['record']['l']

            if earned_points:
                mon_stats[code]['counts']['points'] += 1
                if len(mega_form):
                    mon_stats[code]['forms'][mega_form]['counts']['points'] += 1

            if made_phase_two:
                mon_stats[code]['counts']['phase2'] += 1
                if len(mega_form):
                    mon_stats[code]['forms'][mega_form]['counts']['phase2'] += 1

            if made_cut:
                mon_stats[code]['counts']['cut'] += 1
                if len(mega_form):
                    mon_stats[code]['forms'][mega_form]['counts']['cut'] += 1

    mon_stats = list(mon_stats.values())

    mon_stats.sort(key=lambda mon: mon['counts']['total'], reverse=True)

    sorts = [
        'items',
        'abilities',
        'teras',
        'natures',
        'moves',
        'teammates',
    ]

    for mon_stat in mon_stats:
        mon_stat['distinct'] = len(mon_hashes[mon_stat['code']])
        mon_stat['forms'] = list(mon_stat['forms'].values())

        for sort in sorts:
            mon_stat[sort] = sorted(
                list(mon_stat[sort].values()),
                key=lambda x: (-x['count']['total'], x['name'])
            )

    indent_amt = 2
    separators = None
    if prod:
        indent_amt = None
        separators = (',', ':')

    with open(f"public/data/{year}/{event_code}-usage.json", 'w') as file:
        file.write(json.dumps(mon_stats, indent=indent_amt, separators=separators))


def update_mon_stats(
    mon_stats:dict,
    info_code:str,
    info_name:str,
    stat_category:str,
    earned_points:bool,
    made_phase_two:bool,
    made_cut:bool
):
    if info_code not in mon_stats[stat_category]:
        mon_stats[stat_category][info_code] = {
            'name': info_name,
            'code': info_code,
            'count': {
                "total": 0,
                "points": 0,
                "phase2": 0,
                "cut": 0,
            },
        }
    mon_stats[stat_category][info_code]['count']['total'] += 1
    if earned_points:
        mon_stats[stat_category][info_code]['count']['points'] += 1
    if made_phase_two:
        mon_stats[stat_category][info_code]['count']['phase2'] += 1
    if made_cut:
        mon_stats[stat_category][info_code]['count']['cut'] += 1
