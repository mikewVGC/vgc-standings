
import re

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
process pokedata's json format (where most data comes from)
"""
def process_pokedata_event(data:list, tour_format:list, official_order:list) -> (list, int, dict):

    name_reg = r"^([^\[]+)( {0,1}\[[A-Z]{0,2}\]){0,1}$"

    players = {}
    phase_two_count = 0
    players_in_cut_round = {}
    dupes = []

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

        for mon in player['decklist']:
            mon_name = fix_mon_name(mon['name'])
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
                tera=mon['teratype'],
                ability=mon['ability'],
                item=mon['item'],
                itemcode=make_item_code(mon['item']),
                moves=mon['badges'],
            ))

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
                tbl=opp['table'],
                bye=1 if opp_code == "bye" else 0,
                late=1 if opp_code == "late" else 0,
                phase=phase,
            ))

        made_phase_two = False
        if len(rounds) > tour_format[0]:
            made_phase_two = True
            phase_two_count += 1

        pdata = re.findall(name_reg, player['name'])
        if not len(pdata):
            print('uh oh', player, pdata)

        player_code = make_code(pdata[0][0].strip())
        if player_code in players:
            num = 1
            adjusted_pcode = player_code
            while adjusted_pcode in players:
                adjusted_pcode = f"{player_code}-{num}"
                num += 1
            dupes.append(adjusted_pcode)
            player_code = adjusted_pcode

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
            record={ 'w': player['record']['wins'], 'l': player['record']['losses'] },
            res={
                'self': [],
                'opp': 0,
                'oppopp': 0,
            },
            cut=True if len(rounds) > tour_format[0] + tour_format[1] else False,
            p2=made_phase_two,
            drop=player['drop'],
            points=0,
            team=team,
            rounds=rounds,
        )

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
