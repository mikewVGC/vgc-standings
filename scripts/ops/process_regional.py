
import json
import re

from lib.util import (
    make_code,
    fix_mon_name,
    make_mon_code,
    make_nice_date_str,
)
from lib.tournament import (
    get_tournament_structure,
    calculate_win_pct,
    calculate_res,
    calculate_oppopp,
)
from lib.formes import get_mon_dex_num_from_code, get_mon_alt_from_code

"""
build the standings/matches json
"""
def process_regional(year, code, event_info):
    data = []

    try :
        # thanks to pokedata.ovh for the standings json!
        with open(f"data/majors/{year}/{code}-standings.json", encoding='utf8') as file:
            data = json.loads(file.read())
    except FileNotFoundError:
        print(f"Main standings file not found, maybe this hasn't happened yet? ", end="")
        return False

    player_order = {}
    # thanks to rk9 (would be nice if they published official res etc)
    official_standings = f"data/majors/{year}/{code}-official.txt"
    try:
        with open(official_standings) as file:
            lines = file.read().splitlines()
            for i, line in enumerate(lines):
                matches = re.findall(r"^[0-9]+\. {1}([^\[]+)( {0,1}\[[A-Z]{0,2}\]){0,1}$", line)
                name = matches[0][0].strip()

                player_order[make_code(name)] = i
    except FileNotFoundError:
        print(f"Official standings file not found, skipping. ", end="")

    nameReg = r"^([^\[]+)( {0,1}\[[A-Z]{0,2}\]){0,1}$"

    tour_format = get_tournament_structure(2026, len(data))

    players = {}

    for player in data:
        team = []
        for mon in player['decklist']:
            monName = fix_mon_name(mon['name'])
            monCode = make_mon_code(monName)
            dexNum = get_mon_dex_num_from_code(monCode)

            alt = get_mon_alt_from_code(monCode)
            if alt:
                dexNum = alt

            team.append({
                'name': monName,
                'code': monCode,
                'dex': dexNum,
                'tera': mon['teratype'],
                'ability': mon['ability'],
                'item': mon['item'],
                'moves': mon['badges'],
            })

        rounds = []
        for rnd, opp in player['rounds'].items():
            oppData = re.findall(nameReg, opp['name'])
            oppName = ""
            if len(oppData) > 0:
                oppData = oppData[0]
                oppName = oppData[0].strip()

            oppCode = make_code(oppName)

            phase = 1
            if int(rnd) > tour_format[0] + tour_format[1]:
                phase = 3 # top cut
            elif int(rnd) > tour_format[0]:
                phase = 2  

            rounds.append({
                'round': int(rnd),
                'opp': oppCode if oppCode not in [ 'bye', 'late', 'none' ] else '',
                'res': opp['result'],
                'bye': 1 if oppCode == "bye" else 0,
                'late': 1 if oppCode == "late" else 0,
                'phase': phase,
            })

        pdata = re.findall(nameReg, player['name'])
        if not len(pdata):
            print('uh oh', player, pdata)

        playerCode = make_code(pdata[0][0].strip())

        players[playerCode] = {
            'name': pdata[0][0].strip(),
            'code': playerCode,
            'country': pdata[2] if len(pdata) > 2 else "",
            'place': int(player['placing']),
            'record': { 'w': player['record']['wins'], 'l': player['record']['losses'] },
            'res': {
                'self': [],
                'opp': 0,
                'oppopp': 0,
            },
            'cut': True if len(rounds) > tour_format[0] + tour_format[1] else False,
            'drop': player['drop'],
            'team': team,
            'rounds': rounds,
        }

    # second loop for calculating various resistances
    for player in players:
        players[player]['res']['self'] = calculate_win_pct(player, players, tour_format, players[player]['drop'])

    for player in players:
        players[player]['res']['opp'] = calculate_res(player, players, tour_format)

    for player in players:
        players[player]['res']['oppopp'] = calculate_oppopp(player, players, tour_format)

    for player in players:
        players[player]['rounds'].reverse()

    # fix the order based on rk9 standings
    for player in players:
        # this is likely due to a DQ... but it also allows this
        # to function if the official standings file is missing
        if player not in player_order:
            player_order[player] = len(player_order)

        players[player]['place'] = player_order[player] + 1
        player_order[player] = players[player]

    with open(f"public/data/{year}/{code}.json", 'w') as file:
        file.write(json.dumps({
            "event": event_info,
            "standings": player_order,
        }))

    return True


"""
build the season json... this mostly just copies the corresponding <year>.json
"""
def process_season(year, season_data):
    for code, event_data in season_data.items():
        event_data["dates"] = make_nice_date_str(event_data['start'], event_data['end'])

    season_data = list(season_data.values())
    season_data.reverse()

    with open(f"public/data/{year}.json", 'w') as file:
        file.write(json.dumps(season_data))

