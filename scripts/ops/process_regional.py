
import json
import re
import dataclasses

from ops.processors.pokedata import process_pokedata_event
from ops.processors.rk9scraper import process_rk9scraper_event

from collections import OrderedDict

from lib.util import (
    make_code,
    make_nice_date_str,
)
from lib.tournament import (
    get_tournament_structure,
    get_round_name,
    calculate_win_pct,
    calculate_res,
    calculate_oppopp,
    tour_in_progress,
)
from lib.formes import (
    get_icon_alt,
)

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

"""
build the standings/matches json
"""
def process_regional(year, code, event_info):
    data = []
    data_type = '';

    try :
        # thanks to pokedata.ovh for the standings json!
        with open(f"data/majors/{year}/{code}-standings.json", encoding='utf8') as file:
            data = json.loads(file.read())
            data_type = 'pokedata'
    except FileNotFoundError:
        try:
            with open(f"data/majors/{year}/{code}-roster.json", encoding='utf8') as file:
                data = json.loads(file.read())
                data_type = 'rk9scraper'
        except FileNotFoundError:
            print(f"Main standings file not found, maybe this hasn't happened yet? ", end="")
            return False

    official_order = []
    # thanks to rk9 (would be nice if they published official res etc)
    official_standings = f"data/majors/{year}/{code}-official.txt"
    try:
        with open(official_standings) as file:
            lines = file.read().splitlines()
            for i, line in enumerate(lines):
                matches = re.findall(r"^[0-9]+\. {1}([^\[]+)( {0,1}\[[A-Z]{0,2}\]){0,1}$", line)
                name = matches[0][0].strip()
                name_code = make_code(name)
                num = 1
                while name_code in official_order:
                    name_code = f"{name_code}-{num}"
                    num += 1
                official_order.append(name_code)
    except FileNotFoundError:
        print(f"Official standings not found, skipping. ", end="")

    tour_format = get_tournament_structure(year, len(data), event_info)

    players = {}
    phase_two_count = 0
    players_in_cut_round = {}

    if data_type == 'pokedata':
        players, phase_two_count, players_in_cut_round = process_pokedata_event(data, tour_format, official_order)
    elif data_type == 'rk9scraper':
        players, phase_two_count, players_in_cut_round = process_rk9scraper_event(data, tour_format, official_order, year, code)

    # more loops for calculating various resistances
    for player in players:
        players[player].res['self'] = calculate_win_pct(player, players, tour_format, players[player].drop)

        if players[player].rounds is None:
            continue

        # also repurposing this loop to set round names
        for ri, game in enumerate(players[player].rounds):
            player_count = 0
            if game.round in players_in_cut_round:
                player_count = players_in_cut_round[game.round]
            players[player].rounds[ri].rname = get_round_name(game.round, tour_format, player_count)

    for player in players:
        players[player].res['opp'] = calculate_res(player, players, tour_format)

    for player in players:
        players[player].res['oppopp'] = calculate_oppopp(player, players, tour_format)

    for player in players:
        players[player].rounds.reverse()

    players_ordered = OrderedDict()

    # adjust the order based on rk9 standings
    for pidx, player in enumerate(official_order):
        # set the placement
        players[player].place = pidx + 1
        players_ordered[player] = players[player]

    event_info["dates"] = make_nice_date_str(event_info['start'], event_info['end'])
    event_info["playerCount"] = len(players_ordered)
    event_info["phase2Count"] = phase_two_count

    event_info['in_progress'] = False
    if tour_in_progress(event_info, players_ordered):
        event_info['in_progress'] = True

    with open(f"public/data/{year}/{code}.json", 'w') as file:
        file.write(json.dumps({
            "event": event_info,
            "standings": players_ordered,
        }, cls=EnhancedJSONEncoder, indent=2))

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


"""
this is used with the build_only flag, we check the file exists and
return True/False with the event info data that process_regional added
"""
def was_event_processed(year, event_code):
    event_info = {}

    try:
        with open(f"public/data/{year}/{event_code}.json") as file:
            data = json.loads(file.read())
            event_info = data['event']
    except FileNotFoundError:
        return False, {}

    return True, event_info
