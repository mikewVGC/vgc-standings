
import re
import json

from lib.tournament import (
    player_made_phase_two,
)

from lib.util import (
    make_code,
    fix_mon_name,
    fix_nature,
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

from lib.mon import (
    create_team_member_from_mon,
    MonDictMap,
)

from lib.moves import (
    get_move_info_from_name
)

from ops.format_models import (
    TeamMember,
    Move,
    Round,
    Player,
)

"""
process pokedata's json format (where most data comes from)
"""
def process_pokedata_event(data:list, tour_format:list, official_order:list, event_info:dict) -> (list, int, dict):

    name_reg = r"^([^\[]+)( {0,1}\[[A-Z]{0,2}\]){0,1}$"

    players = {}
    phase_two_count = 0
    players_in_cut_round = {}
    dupes = []

    mon_map = MonDictMap(
        tera="teratype",
        nature="stat_alignment",
        moves="badges",
    )

    for player in data:
        team = []

        if 'decklist' not in player:
            player['decklist'] = []
        if 'rounds' not in player:
            player['rounds'] = {}
        if 'placing' not in player:
            player['placing'] = 0
        if 'record' not in player:
            player['record'] = { 'wins': 0, 'losses': 0 }
        if 'drop' not in player:
            player['drop'] = -1

        # sometimes this happens
        if isinstance(player['decklist'], str):
            try:
                player['decklist'] = json.loads(player['decklist'])
            except json.decoder.JSONDecodeError:
                player['decklist'] = []

        for mon in player['decklist']:
            team.append(create_team_member_from_mon(mon, mon_map, event_info))

        rounds = []
        for rnd, opp in player['rounds'].items():
            opp_data = re.findall(name_reg, opp['name'])
            opp_name = ""
            if len(opp_data) > 0:
                opp_data = opp_data[0]
                opp_name = opp_data[0].strip()

            if opp_name == "R1 BYE":
                opp_name = "BYE"

            opp_code = make_code(opp_name)

            if opp_code == "none" and opp['result'] == "W":
                opp_code = "bye"

            phase = 1
            if int(rnd) > tour_format[0] + tour_format[1]:
                phase = 3 # top cut
            elif int(rnd) > tour_format[0]:
                phase = 2

            if phase == 3:
                if int(rnd) not in players_in_cut_round:
                    players_in_cut_round[int(rnd)] = 0
                players_in_cut_round[int(rnd)] += 1

            rounds.append(Round(
                round=int(rnd),
                rname=rnd,
                opp=opp_code if opp_code not in [ 'bye', 'late', 'none' ] else '',
                res=opp['result'],
                tbl=int(opp['table']),
                bye=1 if opp_code == "bye" else 0,
                late=1 if opp_code == "late" else 0,
                phase=phase,
            ))

        pdata = re.findall(name_reg, player['name'])
        if not len(pdata):
            print('uh oh', player, pdata)

        player_code = make_code(pdata[0][0].strip())
        adjusted_player_code = make_unique_player_code(player_code, players)
        if adjusted_player_code != player_code:
            dupes.append(adjusted_player_code)
            player_code = adjusted_player_code

        player_country = pdata[0][1] if len(pdata[0]) > 1 else ""
        if len(player_country) > 1:
            player_country = player_country[1:-1]

        # flag-icons comes with gb but not uk
        if player_country == "UK":
            player_country = "GB"

        players[player_code] = Player(
            name=pdata[0][0].strip(),
            code=player_code,
            country=player_country.lower(),
            place=int(player['placing']),
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
            cut=True if len(rounds) > tour_format[0] + tour_format[1] else False,
            p2=False,
            drop=player['drop'],
            points=0,
            team=team,
            rounds=rounds,
        )

        if player_made_phase_two(players[player_code], tour_format):
            phase_two_count += 1
            players[player_code].p2 = True

        # add missing players to official order. this is likely due
        # to a DQ or some other issue, but it also allows this
        # to function if the official standings file is missing
        if player_code not in official_order:
            official_order.append(player_code)

    fix_duplicates(players, dupes)

    return players, phase_two_count, players_in_cut_round


"""
this is largely guesswork / doing the first thing that makes sense
"""
def fix_duplicates(players:dict, dupes:list) -> None:
    # fix the opponents of the dupes so they point to the correct player
    for dupe in dupes:
        for rnd in players[dupe].rounds:
            round_num = rnd.round
            opp = rnd.opp
            if len(opp):
                if len(players[opp].rounds) < round_num:
                    # this happens if the dupes play each other
                    # but only during the round
                    for i, rnd in enumerate(players[dupe].rounds):
                        if rnd.opp == opp:
                            break

                    swap = players[dupe].rounds.pop(i)
                    players[opp].rounds.append(swap)

                players[opp].rounds[round_num - 1].opp = dupe


    # go through and see if any players played "themselves"
    # this is hideous, I'm sorry
    for pcode, player in players.items():
        for i, rnd in enumerate(player.rounds):
            found_ctr = 0
            if rnd.opp == pcode:
                # in theory this should always work
                player_dupe = list(filter(lambda d: d.startswith(pcode), dupes))[0]

                # first one we find we'll give to the dupe (which is not necessarily correct)
                if found_ctr == 0:
                    swap = players[pcode].rounds.pop(i)
                    players[player_dupe].rounds.append(swap)
                    found_ctr += 1

                # second one we find we'll assume is the opponent
                if found_ctr == 1:
                    players[pcode].rounds[i].round -= 1
                    players[pcode].rounds[i].opp = player_dupe
