
import json
import re
import dataclasses

from collections import OrderedDict
from pathlib import Path

from ops.processors.pokedata import process_pokedata_event
from ops.processors.rk9scraper import process_rk9scraper_event
from ops.processors.vgcpastes import process_vgcpastes_teamlist
from ops.processors.playlatamscraper import process_playlatamscraper_event
from ops.processors.limitless import process_limitless_event
from ops.processors.victoryroad import process_vr_event

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
from lib.ruleset import Ruleset

from constants import (
    DT_POKEDATA,
    DT_RK9SCRAPER,
    DT_PLAYLATAMSCRAPER,
    DT_LIMITLESS,
    DT_VICTORYROAD,
)

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

"""
build the standings/matches json
"""
def process_regional(
    year:int,
    code:str,
    event_info:dict,
    ruleset:Ruleset | None,
    prod:bool,
    grassroots:bool,
) -> (dict, str):

    try:
        data, data_type = get_data_and_type(year, code)
    except Exception as e:
        print(f"{e} ", end="")

        event_info['processed'] = False
        event_info['status'] = 'upcoming'

        return event_info, ""

    if ruleset:
        event_info['rules'] = ruleset.dump_info()
    elif event_info['rules']:
        event_info['rules'] = Ruleset(**event_info['rules']).dump_info()

    parse_teams = False
    # check for a vgcpastes teamlist to fill in missing teams
    try:
        with open(f"data/majors/{year}/{code}-teams.txt", encoding='utf8') as file:
            parse_teams = True
    except FileNotFoundError:
        ...

    official_order = []
    # official standings usually thanks to rk9 (it would be nice if they published official res too!)
    official_standings = f"data/majors/{year}/{code}-official.txt"
    official_standings_found = False
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
            official_standings_found = True
    except FileNotFoundError:
        print("Official standings not found, skipping. ", end="")

    tour_format = get_tournament_structure(year, len(data), event_info, data_type)

    players = {}
    phase_two_count = 0
    players_in_cut_round = {}

    if data_type == DT_POKEDATA:
        players, phase_two_count, players_in_cut_round = process_pokedata_event(data, tour_format, official_order, event_info)
    elif data_type == DT_RK9SCRAPER:
        players, phase_two_count, players_in_cut_round = process_rk9scraper_event(data, tour_format, official_order, event_info, year, code)
    elif data_type == DT_PLAYLATAMSCRAPER:
        players, phase_two_count, players_in_cut_round = process_playlatamscraper_event(data, tour_format, official_order, event_info, year, code)
    elif data_type == DT_LIMITLESS:
        players, phase_two_count, players_in_cut_round = process_limitless_event(data, tour_format, official_order, event_info)
    elif data_type == DT_VICTORYROAD:
        players, phase_two_count, players_in_cut_round = process_vr_event(data, tour_format, official_order, event_info)

    if parse_teams:
        # this will just add teams to the players
        process_vgcpastes_teamlist(players, event_info, year, code)

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

    # just do the sorting ourselves for worlds 2023 day 1 and non-pokedata + missing official standings
    if (
        (year == 2023 and code == 'worlds-day-1') or 
        (not official_standings_found and data_type in [
                DT_PLAYLATAMSCRAPER,
                DT_RK9SCRAPER,
                DT_LIMITLESS,
            ]
        )
    ):
        custom_sorted = sorted(list(players.values()), key=lambda player: (
            -player.place,
            player.record['w'],
            player.res['self'],
            player.res['opp'],
            player.res['oppopp'],
        ), reverse=True)

        players = {}
        official_order = []
        for p in custom_sorted:
            players[p.code] = p
            official_order.append(p.code)

    # VR should already be sorted
    elif data_type == DT_VICTORYROAD:
        official_order = players


    """
    if (data_type == DT_PLAYLATAMSCRAPER and not official_standings_found):
        c = 1
        for player in players:
            print(f"{c}. {players[player].name}")
            c += 1
    """

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

    event_info['status'] = determine_event_status(event_info, players_ordered)
    event_info['winner'] = ''
    event_info['winner_flag'] = ''
    if 'noWinner' in event_info and event_info['noWinner']:
        event_info['winner'] = '-'
    elif event_info['status'] == 'complete':
        winner = next(iter(players_ordered.values()))
        event_info['winner'] = winner.name
        event_info['winner_flag'] = winner.country

    if event_info['status'] == 'complete' and not event_info['code'].startswith('worlds'):
        # one more loop for points!
        if not grassroots:
            for player in players_ordered.values():
                player.points = get_points_earned(year, len(players_ordered), player.place, event_is_ic)


    indent_amt = 2
    separators = None
    if prod:
        indent_amt = None
        separators = (',', ':')

    with open(f"public/data/{year}/{code}.json", 'w') as file:
        file.write(json.dumps({
            "event": event_info,
            "standings": players_ordered,
        }, cls=EnhancedJSONEncoder, indent=indent_amt, separators=separators))

    return event_info, data_type


"""
figure out which format the data is stored in based on the path
"""
def get_data_and_type(year:int, code:str):
    paths = [
        (f"data/majors/{year}/{code}-standings.json", DT_POKEDATA),
        (f"data/majors/{year}/{code}-roster.json", DT_RK9SCRAPER),
        (f"data/majors/{year}/{code}-roster.pl.json",DT_PLAYLATAMSCRAPER),
        (f"data/majors/grassroots/{code}-standings.json", DT_LIMITLESS),
        (f"data/majors/grassroots/{code}/roster.json", DT_VICTORYROAD),
    ]

    for path_loc, path_type in paths:
        # limitless has the same format as pokedata so...
        if year == "grassroots" and path_type == DT_POKEDATA:
            continue

        file_path = Path(path_loc)
        if file_path.is_file():
            with open(path_loc, encoding='utf8') as file:
                data = json.loads(file.read())
                return data, path_type

    raise Exception("Main standings file not found, maybe this hasn't happened yet?")


"""
build the season json... this mostly just copies the corresponding <year>.json
"""
def process_season(year:int, season_data:dict) -> None:
    for code, event_data in season_data.items():
        event_data["dates"] = make_nice_date_str(event_data['start'], event_data['end'])

    season_data = list(season_data.values())
    season_data = [ event_data for event_data in season_data if 'hide' not in event_data or not event_data['hide'] ]
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
        if event_info['code'] == 'worlds-day-1':
            event_info['winner'] = '-'
        else:
            event_info['winner'] = next(iter(data['standings'].values()))['name']

    return True, event_info
