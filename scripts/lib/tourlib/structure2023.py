
def get_tournament_structure(competitors:int, event_info:dict) -> tuple | None:
    # the first three 2023 regionals had no day 2, instead day 1 rolled into top cut
    if event_info['code'] in ['san-diego', 'liverpool', 'orlando']:
        if competitors >= 513:
            return (10, 0, 5)
        elif competitors >= 410: # liverpool had 487, the other two > 513
            return (9, 0, 5)

    # 2023 - 2024 did not have asym top cut, the last element is # cut rounds (3 = top 8)
    if competitors >= 800:
        return (9, 6, 3)
    elif competitors >= 227:
        return (9, 5, 3)
    elif competitors >= 129:
        return (8, 0, 3)
    elif competitors >= 65:
        return (7, 0, 3)
    elif competitors >= 33:
        return (6, 0, 3)
    elif competitors >= 21:
        return (5, 0, 3)
    elif competitors >= 13:
        return (5, 0, 2)
    elif competitors >= 9:
        return (4, 0, 2)
    elif competitors >= 4:
        return (3, 0, 0)

    return None
