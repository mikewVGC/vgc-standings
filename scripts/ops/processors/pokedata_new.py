
import json

from lib.mon import (
    MonDictMap,
    create_team_member_from_mon,
)
from lib.tournament import (
    player_made_phase_two,
)
from lib.util import (
    make_code,
)

from ops.format_models import (
    Player,
    Round,
)


def process_pokedata_new_event(
    data:list,
    tour_format:list,
    official_order:list,
    event_info:dict,
    year:int,
    code:str,
) -> (dict, int, dict):
    # fetch roster, if available
    roster = []
    try:
        with open(f"data/majors/{year}/{code}-roster.pd.json", encoding='utf8') as file:
            roster = json.loads(file.read())
    except FileNotFoundError:
        ...

    roster_lookup = {}
    if len(roster):
        for i, r in enumerate(roster):
            # filter out non-masters players, sorry jrs and srs
            if r['d'] != 'M':
                continue
            roster_lookup[r['#']] = i

    players = {}
    phase_two_count = 0
    players_in_cut_round = {}

    player_lookup = {}
    for i, player in enumerate(data):
        player_lookup[player['i']] = i

    for i, player in enumerate(data):
        player_code = make_code(player['n'])

        team = []
        if len(roster):
            player_roster_data = roster[roster_lookup[f"{i + 1}"]]

            mon_map = MonDictMap()

            for mon in player_roster_data['tl']:
                team.append(
                    create_team_member_from_mon(
                        {
                            "name": mon[5],
                            "moves": mon[7],
                            "item": mon[6],
                            "ability": mon[4],
                            "tera": mon[3],
                            "nature": mon[2],
                        },
                        mon_map,
                        event_info,
                    )
                )

        player_pairings = []

        if 'r' in player:
            for r, rnd in enumerate(player['r']):
                rnum = r + 1

                [ opp_id, res, table ] = rnd

                if not table:
                    table = 0

                if res == 3:
                    res = 'W'
                elif res == 0:
                    res = 'L'
                elif res == 1:
                    res = 'T'
                else:
                    res = ''

                phase = 1
                if rnum > tour_format[0] + tour_format[1]:
                    phase = 3 # top cut
                elif rnum > tour_format[0]:
                    phase = 2

                if phase == 3:
                    if rnum not in players_in_cut_round:
                        players_in_cut_round[rnum] = 0
                    players_in_cut_round[rnum] += 1

                opp = None
                if opp_id in player_lookup:
                    opp = data[player_lookup[opp_id]]

                player_pairings.append(Round(
                    round=rnum,
                    rname=rnum,
                    opp='' if not opp else make_code(opp['n']),
                    res=res,
                    tbl=int(table),
                    bye=1 if opp_id == -1 and res == 'W' else 0,
                    late=1 if opp_id == -1 and res == 'L' else 0,
                    phase=phase,
                ))

        if player['c'] == "UK":
            player['c'] = "GB"

        if not player['c']:
            player['c'] = ""

        players[player_code] = Player(
            name=player['n'],
            code=player_code,
            country=player['c'].lower(),
            place=(i + 1),
            record={ 'w': player['s'][0], 'l': player['s'][1], 't': player['s'][2] },
            res={
                'self': [],
                'opp': 0,
                'oppopp': 0,
            },
            cut=len(player_pairings) > tour_format[0] + tour_format[1],
            p2=False,
            drop=-1 if not player['d'] else player['d'],
            points=0,
            team=team,
            rounds=player_pairings,
        )

        if player_made_phase_two(players[player_code], tour_format):
            phase_two_count += 1
            players[player_code].p2 = True

        if player_code not in official_order:
            official_order.append(player_code)

    return players, phase_two_count, players_in_cut_round
