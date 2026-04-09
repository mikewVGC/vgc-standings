
import json

from lib.tournament import (
    player_made_phase_two,
    is_mega_format,
)

from lib.util import (
    make_code,
    fix_mon_name,
    make_mon_code,
    make_item_code,
)

from lib.formes import (
    get_mon_data_from_code,
    get_mon_alt_from_code,
    get_icon_alt,
)

from ops.format_models import (
    TeamMember,
    Round,
    Player,
)

"""
process limitless api... this is the easiest one
"""
def process_limitless_event(data:list, tour_format:list, official_order:list, event_info:dict) -> (list, int, dict):
    players = {}
    phase_two_count = 0
    players_in_cut_round = {}

    details = {}
    with open(f"data/majors/limitless/{event_info['code']}-details.json", encoding='utf8') as file:
        details = json.loads(file.read())

    pairings_by_player = get_grouped_pairings(event_info['code'], tour_format, details)

    for player in data:
        player_code = player['player']

        player_pairings = []
        if player_code in pairings_by_player:
            player_pairings = pairings_by_player[player_code]

        team = []

        for mon in player['decklist']:
            mon_code = make_mon_code(mon['id'])
            dex_num, ptype = get_mon_data_from_code(mon_code)

            alt = get_mon_alt_from_code(mon_code)
            if alt:
                dex_num = alt

            team.append(TeamMember(
                name=mon['id'].title(),
                code=mon_code,
                altcode=get_icon_alt(mon_code, mon, is_mega_format(event_info)),
                dex=dex_num,
                ptype=ptype.lower(),
                tera=mon['tera'],
                ability=mon['ability'],
                item=mon['item'],
                itemcode=make_item_code(mon['item']),
                moves=mon['attacks'],
            ))

        players[player_code] = Player(
            name=player['name'],
            code=player_code,
            country="" if not player['country'] else player['country'].lower(),
            place=player['placing'],
            record={
                'w': player['record']['wins'],
                'l': player['record']['losses'],
                't': player['record']['ties'],
            },
            res={
                'self': [],
                'opp': 0,
                'oppopp': 0,
            },
            cut=True if len(player_pairings) > tour_format[0] + tour_format[1] else False,
            p2=False,
            drop=-1 if player['drop'] is None else player['drop'],
            points=0,
            team=team,
            rounds=player_pairings,
        )

        if player_code not in official_order:
            official_order.append(player_code)

        if player_made_phase_two(players[player_code], tour_format):
            phase_two_count += 1
            players[player_code].p2 = True

    for p_code, rounds in pairings_by_player.items():
        # this part is just used to set the players_in_cut_round var
        drop_round = -1
        for r_data in rounds:
            if r_data.drop == 1:
                drop_round = r_data.round
            if r_data.phase == 3:
                rnd = r_data.round
                if rnd not in players_in_cut_round:
                    players_in_cut_round[rnd] = 0
                players_in_cut_round[rnd] += 1

    return players, phase_two_count, players_in_cut_round


def get_grouped_pairings(code:str, tour_format:list, details:dict) -> dict:
    pairings = []
    with open(f"data/majors/limitless/{code}-pairings.json", encoding='utf8') as file:
        pairings = json.loads(file.read())

    pairings_by_player = {}

    # group the pairings by each player
    for match in pairings:
        p1_code = match['player1']
        p2_code = ""
        if 'player2' in match:
            p2_code = match['player2']

        p1_bye = False
        p1_late = False

        # this happens if there's a bye or someone is late
        if not p2_code:
            if match['winner'] == -1:
                p1_late = True
            else:
                # TODO: figure out what happens for bye
                p1_bye = True

        rnd = match['round']
        phase = match['phase']

        if phase > 1:
            cut_round = 2 ** tour_format[2]
            rnum = 0
            while cut_round >= 2:
                cut_round = int(cut_round)
                if match['match'].startswith(f"T{cut_round}"):
                    rnd += rnum
                cut_round /= 2
                rnum += 1

            if phase == 2 and tour_format[1] == 0:
                phase = 3

        for p_code in [ p1_code, p2_code ]:
            if not p_code:
                continue

            if p_code not in pairings_by_player:
                pairings_by_player[p_code] = []

            table_num = -1
            if 'table' in match:
                table_num = match['table']

            pairings_by_player[p_code].append(Round(
                round=rnd,
                rname=f"{rnd}",
                opp=p2_code if p_code == p1_code else p1_code,
                res='W' if match['winner'] == p_code else 'L',
                tbl=table_num,
                bye=int(p1_bye),
                late=int(p1_late),
                phase=phase,
                drop=-1,
            ))

    for pcode, pairings in pairings_by_player.items():
        pairings_by_player[pcode] = sorted(pairings, key=lambda p: p.round)

    return pairings_by_player
