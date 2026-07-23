
def get_tournament_structure(competitors:int, event_info:dict) -> tuple | None:
    if competitors >= 4097:
        return (9, 5, 8)
    elif competitors >= 2049:
        return (9, 4, 8)
    elif competitors >= 1025:
        return (8, 4, 8)
    elif competitors >= 513:
        return (8, 3, 8)
    elif competitors >= 257:
        return (8, 2, 8)
    elif competitors >= 129:
        return (7, 2, 8)
    elif competitors >= 65:
        return (6, 2, 8)
    elif competitors >= 33:
        return (7, 0, 6)
    elif competitors >= 17:
        return (6, 0, 4)
    elif competitors >= 9:
        return (4, 0, 2)
    elif competitors >= 4:
        return (3, 0, 0)

    return None
