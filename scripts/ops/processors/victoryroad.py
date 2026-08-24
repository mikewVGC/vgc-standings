
import json

from operator import itemgetter

from lib.tournament import (
    player_made_phase_two,
)

from lib.util import (
    make_code,
    make_mon_code,
    make_item_code,
    make_unique_player_code,
)

from lib.formes import (
    get_mon_data_from_code,
    get_mon_alt_from_code,
    get_icon_alt,
    get_mon_name_from_code,
)

from lib.moves import (
    get_move_info_from_name
)

from lib.mon import (
    create_team_member_from_mon,
    MonDictMap,
)

from ops.format_models import (
    TeamMember,
    Round,
    Player,
    Move,
)

# this should actually be called process_battlefy_event but... nobody else uses battlefy

def process_vr_event(data:list, tour_format:list, official_order:list, event_info:dict) -> (list, int, dict):
    players = {}
    phase_two_count = 0
    players_in_cut_round = {}

    # hack to fix number players not playing nice
    number_players = {}
    player_id_to_code = {}
    for player in data:
        player_code = make_code(player['name'])
        if player_code.isdigit() and player_code not in number_players:
            number_players[player_code] = f"{player_code}_"
            player['player'] = number_players[player_code]
        elif player_code in number_players:
            print(f"Found dupe 'number' player? '{player['name']}' -> '{player_code}'")
            continue 

        player_id_to_code[player['id']] = player_code

    pairings_by_player = get_grouped_pairings(event_info['code'], tour_format, number_players)

    # Battlefy has full country names instead of codes, which is very annoying
    country_map = {
        "Turkey": "Türkiye",
        "Virgin Islands, British": "British Virgin Islands",
        "South Korea": "Republic of Korea",
        "Viet Nam": "Vietnam",
        "Macedonia": "North Macedonia",
        "Palestinian Territory": "State of Palestine",
        "Czech Republic": "Czechia",
        "Côte D'Ivoire": "Côte D`Ivoire",
    }

    country_data = {}
    with open("data/common/country-codes.json") as file:
        country_data = json.loads(file.read())
        country_data = { value: key for key, value in country_data.items() }
        country_data = { key.lower(): value for key, value in country_data.items() }

    mon_map = MonDictMap(name="species")

    dupe_player_map = {}

    for player in data:
        player_code = make_code(player['name'])
        if player_code.isdigit():
            player_code = f"{player_code}_"

        alt_player_code = make_unique_player_code(player_code, players)
        if alt_player_code != player_code:
            dupe_player_map[alt_player_code] = player_code
            player_code = alt_player_code

        player_pairings = []
        if player['id'] in pairings_by_player:
            player_pairings = pairings_by_player[player['id']]

        wins = 0
        losses = 0
        ties = 0
        for match in player_pairings:
            if match.res == 'W':
                wins += 1
            elif match.res == 'L':
                losses += 1

            if match.opp:
                match.opp = player_id_to_code[match.opp]
                if match.opp in number_players:
                    match.opp = number_players[match.opp]

        team = []
        for mon in player['team']:
            team.append(create_team_member_from_mon(mon, mon_map, event_info))

        # simple replace
        if player['country'] in country_map:
            player['country'] = country_map[player['country']]

        country = ""
        if player['country'].lower() in country_data:
            country = country_data[player['country'].lower()]
        elif len(player['country']) > 0:
            print(f"Couldn't find country code match for {player['country']}")

        players[player_code] = Player(
            name=player['name'],
            code=player_code,
            country=country.lower(),
            place=1,
            record={
                'w': wins,
                'l': losses,
                't': ties,
            },
            res={
                'self': [],
                'opp': 0,
                'oppopp': 0,
            },
            cut=True if len(player_pairings) > tour_format[0] + tour_format[1] else False,
            p2=False,
            drop=-1,
            points=0,
            team=team,
            rounds=player_pairings,
        )

        if player_made_phase_two(players[player_code], tour_format):
            phase_two_count += 1
            players[player_code].p2 = True

    # for dupe-coded players who had their code changes (player-name -> player-name-1)
    # we need to fix their code on all their opponent's opponents list
    for new_code, old_code in dupe_player_map.items():
        for pl_round in players[new_code].rounds:
            opp_code = pl_round.opp
            opp_rnum = pl_round.round

            if not len(opp_code) or opp_code not in players:
                # probably a bye, we can skip
                continue

            for opp in players[opp_code].rounds:
                if opp.round == opp_rnum:
                    opp.opp = new_code
                    break

    # this part is just used to set the players_in_cut_round var
    for p_code, rounds in pairings_by_player.items():
        for r_data in rounds:
            if r_data.phase != 3:
                continue
            rnd = r_data.round
            if rnd not in players_in_cut_round:
                players_in_cut_round[rnd] = 0
            players_in_cut_round[rnd] += 1

    return players, phase_two_count, players_in_cut_round


def get_grouped_pairings(event_code:str, tour_format, number_players):
    pairings = []
    stages = []
    with open(f"data/majors/grassroots/{event_code}/pairings.json", encoding='utf8') as file:
        pairings, stages = itemgetter('pairings', 'stages')(json.loads(file.read()))

    pairings_by_player = {}

    max_phase_round = 0

    for match in pairings:
        p1 = match['player1']
        p2 = match['player2']

        real_round_num = match['round']

        for pl in [ p1, p2 ]:
            if pl['id'] not in pairings_by_player:
                pairings_by_player[pl['id']] = []

            if match['round'] > max_phase_round:
                max_phase_round = match['round']

            phase = 1
            for i, stage in enumerate(stages):
                if match['stage'] == stage['id']:
                    phase = 1
                    if match['round'] > tour_format[0]:
                        phase = 2
                    if stage['type'] == "elimination":
                        phase = 3
                        real_round_num = match['round'] + max_phase_round

            pairings_by_player[pl['id']].append(Round(
                round=real_round_num,
                rname=f"{real_round_num}",
                opp=p2['id'] if pl['id'] == p1['id'] else p1['id'],
                res='W' if pl['winner'] else 'L',
                tbl=0,
                bye=int(pl['bye']),
                late=False,
                phase=phase,
                drop=-1,
            ))

    return pairings_by_player
