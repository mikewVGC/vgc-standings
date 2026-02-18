
"""
Calculate win % through a specific round (-1 to calculate all rounds)
Note that since top cut doesn't count towards res, this will never
go beyond tour_format[0] + tour_format[1]
"""
def calculate_win_pct(player:str, players:dict, tour_format:list, through_round:int = -1) -> float:
    matches = players[player].rounds

    if through_round == -1:
        through_round = min(len(matches), tour_format[0] + tour_format[1])

    total = 0
    wins = 0
    
    for match in matches[:through_round]:
        if match.bye:
            continue

        total += 1
        if match.res == "W":
            wins += 1

    pct = .25
    if total > 0:
        pct = wins / total

    # players who drop can't have a win pct > 75%
    if (
        players[player].drop != -1 and
        players[player].drop != tour_format[0] and
        players[player].drop != tour_format[0] + tour_format[1]
    ):
        pct = min(pct, .75)

    # minimum win pct is 25% regardless of wins
    return max(pct, .25)


"""
Calculate res through a specific round (-1 for all round)
Same rule applies as in the win pct calc
"""
def calculate_res(player:str, players:dict, tour_format:list, through_round:int = -1) -> float:
    matches = players[player].rounds

    if through_round == -1:
        through_round = min(len(matches), tour_format[0] + tour_format[1])

    last_round_played = min(len(matches), tour_format[0] + tour_format[1])

    match_count = 0
    total_pct = 0

    for match in matches[:through_round]:
        if match.bye or match.opp == '':
            continue

        opp = match.opp
        if not opp or opp not in players:
            print(f"[res] Missing opponent '{opp}' for {player} (round {match.round})")
            continue

        pct = calculate_win_pct(opp, players, tour_format, min(last_round_played, through_round))
        total_pct += pct
        match_count += 1

    if match_count == 0:
        return .25

    return total_pct / match_count


"""
Calculate oppopp %
"""
def calculate_oppopp(player:str, players:dict, tour_format:list, through_round:int = -1) -> float:
    matches = players[player].rounds

    if through_round == -1:
        through_round = min(len(matches), tour_format[0] + tour_format[1])

    last_round_played = min(len(matches), tour_format[0] + tour_format[1])

    match_count = 0
    total_pct = 0

    for match in matches[:through_round]:
        if match.bye or match.opp == '':
            continue

        opp = match.opp
        if not opp or opp not in players:
            print(f"[opp] Missing opponent '{opp}' for {player} (round {match.round})")
            continue

        pct = calculate_res(opp, players, tour_format, min(last_round_played, through_round))
        total_pct += pct
        match_count += 1

    if match_count == 0:
        return .25

    return total_pct / match_count
