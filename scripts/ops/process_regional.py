
import json
import re
import dataclasses

from collections import OrderedDict

from ops.processors.pokedata import process_pokedata_event
from ops.processors.rk9scraper import process_rk9scraper_event
from ops.processors.vgcpastes import process_vgcpastes_teamlist
from ops.processors.playlatamscraper import process_playlatamscraper_event

from lib.util import (
    make_code,
    make_nice_date_str,
)
from lib.tournament import (
    get_tournament_structure,
    get_round_name,
    determine_event_status,
    get_points_earned,
    get_points_threshold,
)
from lib.res import (
    calculate_win_pct,
    calculate_res,
    calculate_oppopp
)

DT_POKEDATA = 'pokedata'
DT_RK9SCRAPER = 'rk9scraper'
DT_PLAYLATAMSCRAPER = 'playlatamscraper'

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

"""
build the standings/matches json
"""
def process_regional(year:int, code:str, event_info:dict) -> dict:
    data = []
    data_type = ''
    parse_teams = False

    try :
        # thanks to pokedata.ovh for the standings json!
        with open(f"data/majors/{year}/{code}-standings.json", encoding='utf8') as file:
            data = json.loads(file.read())
            data_type = DT_POKEDATA
    except FileNotFoundError:
        try:
            with open(f"data/majors/{year}/{code}-roster.json", encoding='utf8') as file:
                data = json.loads(file.read())
                data_type = DT_RK9SCRAPER
        except FileNotFoundError:
            try:
                with open(f"data/majors/{year}/{code}-roster.pl.json", encoding='utf8') as file:
                    data = json.loads(file.read())
                    data_type = DT_PLAYLATAMSCRAPER
            except FileNotFoundError:
                print("Main standings file not found, maybe this hasn't happened yet? ", end="")
                event_info['processed'] = False
                event_info['status'] = 'upcoming'

                return event_info

    # check for a vgcpastes teamlist to fill in missing teams
    try:
        with open(f"data/majors/{year}/{code}-teams.txt", encoding='utf8') as file:
            parse_teams = True
    except FileNotFoundError:
        ...

    official_order = []
    # thanks to rk9 (would be nice if they published official res!)
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
        print("Official standings not found, skipping. ", end="")

    tour_format = get_tournament_structure(year, len(data), event_info)

    players = {}
    phase_two_count = 0
    players_in_cut_round = {}

    if data_type == DT_POKEDATA:
        players, phase_two_count, players_in_cut_round = process_pokedata_event(data, tour_format, official_order)
    elif data_type == DT_RK9SCRAPER:
        players, phase_two_count, players_in_cut_round = process_rk9scraper_event(data, tour_format, official_order, year, code)
    elif data_type == DT_PLAYLATAMSCRAPER:
        players, phase_two_count, players_in_cut_round = process_playlatamscraper_event(data, tour_format, official_order, year, code)

    if parse_teams:
        # this will just add teams to the players
        process_vgcpastes_teamlist(players, year, code)

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

    # just do the sorting ourselves for worlds 2023 day 1
    if year == 2023 and code == 'worlds-day-1':
        sorted_worlds = sorted(list(players.values()), key=lambda player: (
            player.record['w'],
            player.res['self'],
            player.res['opp'],
            player.res['oppopp'],
        ), reverse=True)

        players = {}
        official_order = []
        for p in sorted_worlds:
            players[p.code] = p
            official_order.append(p.code)

    # adjust the order based on rk9 standings
    for pidx, player in enumerate(official_order):
        # set the placement
        players[player].place = pidx + 1
        players_ordered[player] = players[player]

    event_is_ic = True if event_info['code'] in ('ocic', 'laic', 'euic', 'naic') else False

    event_info['processed'] = True
    event_info['dates'] = make_nice_date_str(event_info['start'], event_info['end'])
    event_info['points'] = get_points_threshold(year, len(players_ordered))
    event_info['playerCount'] = len(players_ordered)
    event_info['phase2Count'] = phase_two_count
    event_info['cutCount'] = 0
    # worlds day 1 doesn't have cut
    if len(players_in_cut_round.values()):
        event_info['cutCount'] = list(players_in_cut_round.values())[0]

    event_info['status'] = determine_event_status(event_info)
    if event_info['status'] == 'complete':
        event_info['winner'] = next(iter(players_ordered.values())).name

        # one more loop for points!
        for player in players_ordered.values():
            player.points = get_points_earned(year, len(players_ordered), player.place, event_is_ic)

    with open(f"public/data/{year}/{code}.json", 'w') as file:
        file.write(json.dumps({
            "event": event_info,
            "standings": players_ordered,
        }, cls=EnhancedJSONEncoder, indent=2))

    return event_info


"""
build the season json... this mostly just copies the corresponding <year>.json
"""
def process_season(year:int, season_data:dict) -> None:
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
def was_event_processed(year:int, event_code:str) -> (bool, dict):
    event_info = {}

    try:
        with open(f"public/data/{year}/{event_code}.json") as file:
            data = json.loads(file.read())
            event_info = data['event']
    except FileNotFoundError:
        return False, { 'processed': False, 'status': 'upcoming' }

    event_info['processed'] = True
    event_info['status'] = determine_event_status(event_info)
    event_info['winner'] = ''
    if event_info['status'] == 'complete':
        event_info['winner'] = next(iter(data['standings'].values()))['name']

    return True, event_info
