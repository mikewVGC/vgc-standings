
# returns (day 1 rounds, day 2 rounds, top cut min)
def get_tournament_structure(season, competitors):
    if season == 2026:
        if competitors >= 4097:
            return (9, 6, 8)
        elif competitors >= 2049:
            return (8, 6, 8)
        elif competitors >= 1025:
            return (8, 5, 8)
        elif competitors >= 513:
            return (8, 4, 8)
        elif competitors >= 257:
            return (8, 3, 8)
        elif competitors >= 129:
            return (8, 2, 8)
        elif competitors >= 65:
            return (7, 2, 8)
        elif competitors >= 33:
            return (7, 0, 6)
        elif competitors >= 17:
            return (6, 0, 4)
        elif competitors >= 9:
            return (4, 0, 2)
        elif competitors >= 4:
            return (3, 0, 0)

    return None


# get "fancy" round name: Cut, T8 etc
# this only works for 2026 asym cut (max 16)
def get_round_name(rnd, tour_format):
    last_swiss = tour_format[0] + tour_format[1]
    if int(rnd) <= last_swiss:
        return rnd

    if int(rnd) == last_swiss + 1:
        return "Top Cut"
    if int(rnd) == last_swiss + 2:
        return "Top 8"
    if int(rnd) == last_swiss + 3:
        return "Top 4"
    if int(rnd) == last_swiss + 4:
        return "Finals"

    return rnd


"""
In order to get accurate res, we need to calculate both day 1 and day 2 win pct
"""
def calculate_win_pct(player, players, tour_format, drop_round = None):
    phases = [
        [ 0, tour_format[0] ],
    ]

    # if they made day 2, add that
    if players[player]['drop'] == -1 or players[player]['drop'] > tour_format[0]:
        phases.append([ 0, tour_format[0] + tour_format[1] ])

    results = []

    for phase in phases:
        matches = players[player]['rounds']
        wins = 0
        total = 0
        for match in matches[phase[0]:phase[1]]:
            if match['bye']:
                continue

            total += 1
            if match['res'] == "W":
                wins += 1

            if drop_round != None and match['round'] == drop_round:
                break

        pct = .25
        if total > 0:
            pct = wins / total

        # players who drop can't have a win pct > 75%
        if (
            players[player]['drop'] != -1 and
            players[player]['drop'] != tour_format[0] and
            players[player]['drop'] != tour_format[0] + tour_format[1]
        ):
            pct = min(pct, .75)

        # minimum win pct is 25% regardless of wins
        results.append(max(pct, .25))

    return results


"""
After a lot of trial and error, here is how res works:

* All players have two win pcts, one for day 1, another for day 1 + day 2 (assuming they made day 2)
* When calculating res, you take the win% of matching phases. Example:
    * Players A, B, and C all played each other
    * Player A went 6 - 2 in d1, 2 -2 in d2
    * Player B went 5 - 3 in d1
    * Player C went 7 - 1 in d1, 3 - 1 in d2
    * When calculating Player B's res, you use:
        * .75 for Player A's win pct (6 - 2 record)
        * .875 for Player C's win pct (7 - 1 record)
    * When calculating Player A's res, you use:
        * .625 for Player B pct (5 - 3 record)
        * .833 for Player Cs' win pct (10 - 2 record)
    * Notably when a player drops you need to get their 
"""
def calculate_res(player, players, tour_format):
    matches = players[player]['rounds']
    total = 0
    match_count = 0

    made_phase_two = False
    if players[player]['drop'] == -1 or players[player]['drop'] > tour_format[0]:
        made_phase_two = True

    for match in matches:
        if match['bye'] or match['opp'] == '':
            continue

        opp = match['opp']
        if not opp or opp not in players:
            print(f"[res] Missing opponent '{opp}' for {player} (round {match['round']})")
            continue

        opp_phase = 0
        opp_made_phase_two = players[opp]['drop'] == -1 or players[opp]['drop'] > tour_format[0]
        if made_phase_two and opp_made_phase_two:
            opp_phase = 1

        pct = players[opp]['res']['self'][opp_phase]
        match_count += 1

        if players[player]['drop'] != -1 and players[player]['drop'] < tour_format[0]:
            # recalculate opponents for players who dropped during day 1
            pct = calculate_win_pct(opp, players, tour_format, players[player]['drop'])[0]
        elif opp_made_phase_two and players[player]['drop'] != -1 and players[player]['drop'] < tour_format[0] + tour_format[1]:
            # players who dropped during day 2
            pct = calculate_win_pct(opp, players, tour_format, players[player]['drop'])[1]

        total += pct

    if match_count == 0:
        return .25

    return max(total / match_count, .25)


"""
ugh... this mostly works but there are some instances where it doesn't match up with
the official standings / order on rk9 ... I also need to validate the rk9 order matches
the one on pokemon.com
"""
def calculate_oppopp(player, players, tour_format):
    matches = players[player]['rounds']
    made_phase_two = players[player]['drop'] == -1 or players[player]['drop'] > tour_format[0]

    total_pct = 0
    match_count = 0

    for match in matches:
        if match['bye'] or match['opp'] == '':
            continue

        opp = match['opp']
        opp_matches = players[opp]['rounds']

        oppopp_total_pct = 0
        oppopp_match_count = 0

        for opp_match in opp_matches:
            if opp_match['bye'] or opp_match['opp'] == '':
                continue

            oppopp = opp_match['opp']
            if not oppopp or oppopp not in players:
                print(f"[oppopp] Missing opponent '{oppopp}' for {opp} (round {opp_match['round']})")
                continue

            oppopp_phase_two = players[oppopp]['drop'] == -1 or players[oppopp]['drop'] > tour_format[0]

            pct = players[oppopp]['res']['self'][1 if oppopp_phase_two else 0]

            if players[opp]['drop'] != -1 and players[opp]['drop'] < tour_format[0]:
                # recalculate opponents for players who dropped during day 1
                pct = calculate_win_pct(oppopp, players, tour_format, players[player]['drop'])[0]
            elif oppopp_phase_two and players[opp]['drop'] != -1 and players[opp]['drop'] < tour_format[0] + tour_format[1]:
                # players who dropped during day 2
                pct = calculate_win_pct(oppopp, players, tour_format, players[player]['drop'])[1]

            oppopp_total_pct += pct
            oppopp_match_count += 1

        total_pct += oppopp_total_pct / oppopp_match_count
        match_count += 1

    return total_pct / match_count
