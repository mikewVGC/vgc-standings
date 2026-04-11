
import json
import math
import re

"""
figrue out the tour_structure for a limitless tour
"""
def determine_tournament_structure(season:int, competitors:int, event_info:dict) -> tuple | None:
    details = {}
    with open(f"data/majors/limitless/{event_info['code']}-details.json", encoding='utf8') as file:
        details = json.loads(file.read())

    swiss_rounds_p1 = 0
    swiss_rounds_p2 = 0
    for phase in details['phases']:
        if phase['type'] == "SWISS":
            if phase['phase'] == 1:
                swiss_rounds_p1 += phase['rounds']
            if phase['phase'] != 1:
                swiss_rounds_p2 += phase['rounds']

    pairings = []
    with open(f"data/majors/limitless/{event_info['code']}-pairings.json", encoding='utf8') as file:
        pairings = json.loads(file.read())

    # need to figure out the size of cut because limitless doesn't say
    max_cut = 0
    for match in pairings:
        if match['phase'] == 1:
            continue

        res = re.findall(r"^T([0-9]{1,3})-[0-9]{1,2}$", match['match'])
        if int(res[0]) > max_cut:
            max_cut = int(res[0])

    cut_rounds = math.floor(math.log2(max_cut))

    return (swiss_rounds_p1, swiss_rounds_p2, cut_rounds)
