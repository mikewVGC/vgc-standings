
def get_tournament_structure(competitors:int, event_info:dict) -> tuple | None:
    # lima and bogota 2024 are a little messed up because they're mixed divisioon
    if event_info['code'] in ['lima', 'bogota']:
        return (6, 0, 3)

    # notably 2024 worlds uses the 2025 structure
    if event_info['code'] == "worlds":
        return (8, 3, 8)

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
