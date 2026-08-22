
import json

def determine_tournament_structure(season:int, competitors:int, event_info:dict) -> tuple | None:

    details = {}
    with open(f"data/majors/grassroots/{event_info['code']}/info.json", encoding='utf8') as file:
        details = json.loads(file.read())

    swiss_rounds_p1 = 0
    swiss_rounds_p2 = 0
    cut_rounds = 0

    for stage in details['stages']:
        if stage['bracket']['type'] == "swiss":
            if swiss_rounds_p1 == 0:
                swiss_rounds_p1 = stage['bracket']['roundsCount']
            elif swiss_rounds_p2 == 0:
                swiss_rounds_p2 = stage['bracket']['roundsCount']
        if stage['bracket']['type'] == "elimination":
            cut_rounds = stage['bracket']['roundsCount']

    # vr tours all use the same structure as the official circuit, however battlefy doesn't
    # have a concept of phase 2 when these are set up, so we have to fudge it a little
    max_phase_one_rounds = 8
    if competitors > 4097:
        max_phase_one_rounds = 9

    swiss_rounds_p2 = swiss_rounds_p1 - max_phase_one_rounds
    swiss_rounds_p1 = max_phase_one_rounds

    return (swiss_rounds_p1, swiss_rounds_p2, cut_rounds)
