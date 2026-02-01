
import json

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

def process_playlatamscraper_event(data, tour_format, official_order, year, code):
    players = {}
    phase_two_count = 0
    players_in_cut_round = {}

    pairings_by_player = get_grouped_pairings(year, code, tour_format)

    dupe_names = {}
    dupes = []

    for player in data:
        team = []

        for mon in player['team']:
            if mon['species'] == 'Ursaluna [Bloodmoon Ursaluna]':
                mon['species'] = 'Ursaluna [Bloodmoon Form]'

            mon_name = fix_mon_name(mon['species'])
            mon_code = make_mon_code(mon_name)
            dex_num, ptype = get_mon_data_from_code(mon_code)

            alt = get_mon_alt_from_code(mon_code)
            if alt:
                dex_num = alt

            team.append(TeamMember(
                name=mon_name,
                code=mon_code,
                altcode=get_icon_alt(mon_code, mon),
                dex=dex_num,
                ptype=ptype.lower(),
                tera=mon['tera'],
                ability=mon['ability'],
                item=mon['item'],
                itemcode=make_item_code(mon['item']),
                moves=mon['moves'],
            ))

        player_code = make_code(player['name'])
        op_code = player_code

        if player_code in players:
            if op_code not in dupe_names:
                dupe_names[op_code] = []

            num = 1
            while player_code in players:
                player_code = f"{player_code}-{num}"
                num += 1
            
            dupe_names[op_code].append(player_code)
            dupes.append(player_code)

        if player_code not in official_order:
            official_order.append(player_code)

        rounds = []
        if player_code in pairings_by_player:
            rounds = pairings_by_player[player_code]

        made_phase_two = False
        if len(rounds) > tour_format[0]:
            made_phase_two = True
            phase_two_count += 1

        player_pairings = []
        if player_code in pairings_by_player:
            player_pairings = pairings_by_player[player_code]
        elif op_code in dupe_names:
            deduped_name = dupe_names[op_code].pop()
            player_pairings = pairings_by_player[deduped_name]

        wins = 0
        losses = 0
        for game in player_pairings:
            if game.res == 'W':
                wins +=1
            elif game.res == 'L':
                losses += 1

        players[player_code] = Player(
            name=player['name'],
            code=player_code,
            country=player['country'],
            place='',
            record={ 'w': wins, 'l': losses },
            res={
                'self': [],
                'opp': 0,
                'oppopp': 0,
            },
            cut=True if len(player_pairings) > tour_format[0] + tour_format[1] else False,
            p2=made_phase_two,
            drop=-1,
            team=team,
            rounds=player_pairings,
        )

    for p_code, rounds in pairings_by_player.items():
        # this part is just used to set the players_in_cut_round var
        for r_data in rounds:
            if r_data.phase == 3:
                rnd = r_data.round
                if rnd not in players_in_cut_round:
                    players_in_cut_round[rnd] = 0
                players_in_cut_round[rnd] += 1

    # fix the opponents of the dupes (they need to point to the right player)
    for dupe in dupes:
        for rnd in players[dupe].rounds:
            round_num = rnd.round
            opp = rnd.opp
            if len(opp):
                players[opp].rounds[round_num - 1].opp = dupe

    # playlatam doesn't have standings usually, so we have to dump official standings and fix them
    sorted_players = sorted(list(players.values()), key=lambda player: (
        player.record['w'],
        player.res['self'],
        player.res['opp'],
        player.res['oppopp']
    ), reverse=True)

    # uncommebnt this for a list (doesn't take cut into account)
    #for i, player in enumerate(sorted_players):
    #    print(f"{i + 1}. {player.name}")

    return players, phase_two_count, players_in_cut_round


def get_grouped_pairings(year, code, tour_format):
    pairings = []
    with open(f"data/majors/{year}/{code}-pairings.pl.json", encoding='utf8') as file:
        pairings = json.loads(file.read())

    pairings_by_player = {}

    # group the pairings by each player
    for p_round in pairings:
        for match in p_round:
            p1 = match['p1']
            p2 = match['p2']

            p1_code = make_code(p1)
            p2_code = make_code(p2)

            p1_bye = False
            p1_late = False

            # this happens if there's a bye or someone is late
            if len(p2_code) == 0:
                if match['winner'] == p1:
                    p1_bye = True
                else:
                    p1_late = True

            rnd = match['round']

            phase = 1
            if rnd > tour_format[0] + tour_format[1]:
                phase = 3 # top cut
            elif rnd > tour_format[0]:
                phase = 2

            for i, p_code in enumerate([ p1_code, p2_code ]):
                if len(p_code) == 0:
                    continue
                if p_code not in pairings_by_player:
                    pairings_by_player[p_code] = []

            for player_num in [ 'p1', 'p2' ]:
                p_code = p1_code if player_num == 'p1' else p2_code
                if len(p_code) == 0:
                    continue

                pp_code = p_code
                num = 1
                if len(pairings_by_player[p_code]) == rnd:
                    while pp_code not in pairings_by_player or len(pairings_by_player[pp_code]) == rnd:
                        if pp_code not in pairings_by_player:
                            pairings_by_player[pp_code] = []
                            break
                        pp_code = f"{p_code}-{num}"
                        num += 1

                result = ''
                if match[player_num] == match['winner']:
                    result = 'W'
                else:
                    result = 'L'

                pairings_by_player[pp_code].append(Round(
                    round=rnd,
                    rname=f"{rnd}",
                    opp=p2_code if p_code == p1_code else p1_code,
                    res=result,
                    tbl=match['table'],
                    bye=int(p1_bye),
                    late=int(p1_late),
                    phase=phase,
                ))

    return pairings_by_player
