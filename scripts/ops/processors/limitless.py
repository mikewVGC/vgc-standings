
import json
import math
import re

from lib.tournament import (
    player_made_phase_two,
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
    get_mon_name_from_code,
    get_mon_base_form_from_code,
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

    # limitless allows numerical names for players, which messes up the front-end... don't ask
    number_players = {}
    for player in data:
        player_code = player['player']
        if player_code.isdigit():
            number_players[player_code] = f"{player_code}_"
            player['player'] = number_players[player_code]

    pairings_by_player = get_grouped_pairings(event_info['code'], tour_format, details, number_players)

    for player in data:
        player_code = player['player']

        player_pairings = []
        if player_code in pairings_by_player:
            player_pairings = pairings_by_player[player_code]

        team = []

        for mon in player['decklist']:
            # limitless data requires a lot of normalization because it accepts both
            # the base form and mega form for teamsheets... I don't think other
            # data sources will do this, so this section will likely be less convoluted

            mon_code = make_mon_code(mon['id'])

            mon_name = mon['id'].title()

            # this will get the non-mega version if they've submitted the mega
            # this will cause the ability to be incorrect if it changes after mega
            base_form = get_mon_base_form_from_code(mon_code)
            if base_form:
                mon_code = make_mon_code(base_form)
                mon_name = base_form

            # limitless also doesn't support eternal floette so we have to assume
            if mon_code == 'floette' and mon['item'] == 'Floettite' or mon_code == 'floettemega':
                mon_code = make_mon_code('floette-eternal')
                mon_name = 'Floette-Eternal'

            dex_num, ptype = get_mon_data_from_code(mon_code)

            tera_type = "" if 'tera' not in mon else mon['tera']
            if not event_info['rules']['tera']:
                tera_type = ""

            mon_alt_code = get_icon_alt(mon_code, mon, event_info['rules']['mega'])

            mon_alt_name = ""
            if mon_alt_code:
                mon_alt_name = get_mon_name_from_code(mon_alt_code)

            alt = ""
            if mon_alt_code:
                alt = get_mon_alt_from_code(mon_alt_code)
            else:
                alt = get_mon_alt_from_code(mon_code)

            if alt:
                dex_num = alt

            team.append(TeamMember(
                name=mon_name,
                code=mon_code,
                altname=mon_alt_name,
                altcode=mon_alt_code,
                dex=dex_num,
                ptype=ptype.lower(),
                tera=str(tera_type),
                ability=mon['ability'],
                item=mon['item'],
                itemcode=make_item_code(mon['item']),
                moves=mon['attacks'],
            ))

        place = player['placing']
        if place == None:
            place = 1000

        players[player_code] = Player(
            name=player['name'],
            code=player_code,
            country="" if not player['country'] else player['country'].lower(),
            place=place,
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


def get_grouped_pairings(code:str, tour_format:list, details:dict, number_players:dict) -> dict:
    pairings = []
    with open(f"data/majors/limitless/{code}-pairings.json", encoding='utf8') as file:
        pairings = json.loads(file.read())

    pairings_by_player = {}

    swiss_rounds_p1 = 0
    swiss_rounds_p2 = 0
    for phase in details['phases']:
        if phase['type'] == "SWISS":
            if phase['phase'] == 1:
                swiss_rounds_p1 += phase['rounds']
            if phase['phase'] != 1:
                swiss_rounds_p2 += phase['rounds']

    # first pass so we can figure out the size of cut
    max_cut = 0
    max_phase = 1
    cut_rounds = 0

    for match in pairings:
        if match['phase'] > max_phase:
            max_phase = match['phase']

        if match['phase'] == 1:
            continue
        if 'match' not in match:
            continue

        res = re.findall(r"^T([0-9]{1,3})-[0-9]{1,2}$", match['match'])
        if int(res[0]) > max_cut:
            max_cut = int(res[0])

    if max_cut > 0:
        cut_rounds = math.floor(math.log2(max_cut))
    else:
        cut_players = {}
        cut_count = 0
        for match in pairings:
            if match['phase'] != max_phase:
                continue

        if match['player1']:
            cut_players[match['player1']] = True
        if match['player2']:
            cut_players[match['player2']] = True

        max_cut = len(cut_players.keys())

    tour_format = (swiss_rounds_p1, swiss_rounds_p2, cut_rounds)

    # group the pairings by each player
    for match in pairings:
        p1_code = match['player1']
        p2_code = ""
        if 'player2' in match:
            p2_code = match['player2']

        if p1_code in number_players:
            p1_code = number_players[p1_code]

        if len(p2_code) and p2_code in number_players:
            p2_code = number_players[p2_code]

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
            cut_round = 2 ** cut_rounds
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

            winner = match['winner']
            if winner in number_players:
                winner = number_players[winner]

            pairings_by_player[p_code].append(Round(
                round=rnd,
                rname=f"{rnd}",
                opp=p2_code if p_code == p1_code else p1_code,
                res='W' if winner == p_code else 'L',
                tbl=table_num,
                bye=int(p1_bye),
                late=int(p1_late),
                phase=phase,
                drop=-1,
            ))

    for pcode, pairings in pairings_by_player.items():
        pairings_by_player[pcode] = sorted(pairings, key=lambda p: p.round)

    return pairings_by_player
