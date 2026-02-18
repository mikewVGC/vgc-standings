from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

"""
returns (day 1 rounds, day 2 rounds, top cut min)
I don't think actually uses the third value yet?
"""
def get_tournament_structure(season:int, competitors:int, event_info:dict) -> tuple | None:
    # the first three 2023 regionals had no day 2, instead day 1 rolled into top cut
    if season == 2023 and event_info['code'] in ['san-diego', 'liverpool', 'orlando']:
        if competitors >= 513:
            return (10, 0, 5)
        elif competitors >= 410: # liverpool had 487, the other two > 513
            return (9, 0, 5)

    # 2023 - 2024 did not have asym top cut, the last element is # cut rounds (3 = top 8)
    if season == 2023 or (season == 2024 and event_info['code'] != "worlds"):
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

    # notably 2024 worlds uses the 2025 structure
    if season == 2025 or (season == 2024 and event_info['code'] == "worlds"):
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


"""
given a number of competitors, return how many will earn points
"""
def get_points_threshold(season:int, competitors:int) -> int | None:
    if season == 2023:
        if competitors >= 800:
            return 256
        if competitors >= 400:
            return 128
        if competitors >= 200:
            return 64
        if competitors >= 100:
            return 32
        if competitors >= 48:
            return 16
        if competitors >= 8:
            return 8

    if season == 2024:
        if competitors >= 1024:
            return 512
        if competitors >= 512:
            return 256
        if competitors >= 256:
            return 128
        if competitors >= 128:
            return 64
        if competitors >= 80:
            return 32
        if competitors >= 48:
            return 16
        if competitors >= 8:
            return 8

    if season == 2025 or season == 2026:
        if competitors >= 2049:
            return 1024
        if competitors >= 1025:
            return 512
        if competitors >= 513:
            return 256
        if competitors >= 257:
            return 128
        if competitors >= 129:
            return 64
        if competitors >= 65:
            return 32
        if competitors >= 33:
            return 16
        if competitors >= 17:
            return 8
        if competitors >= 8:
            return 4
        if competitors >= 4:
            return 2

    return None

"""
Get the champ points a player earned based on # of competitors and placement
"""
def get_points_earned(season:int, competitors:int, place:int, ic:bool = False) -> int | None:
    # below the threshold let's just not bother
    if place > get_points_threshold(season, competitors):
        return 0

    if season == 2023:
        if place == 1:
            return 500 if ic else 200
        elif place == 2:
            return 400 if ic else 160
        elif place <= 4:
            return 320 if ic else 130
        elif place <= 8:
            return 250 if ic else 100
        elif place <= 16 and competitors >= 48:
            return 200 if ic else 80
        elif place <= 32 and competitors >= 100:
            return 160 if ic else 60
        elif place <= 64 and competitors >= 200:
            return 130 if ic else 50
        elif place <= 128 and competitors >= 400:
            return 100 if ic else 40
        elif place <= 256 and competitors >= 800:
            return 80 if ic else 30
        elif place <= 512 and competitors >= 1600 and ic:
            return 60

    if season == 2024:
        if place == 1:
            return 500 if ic else 200
        elif place == 2:
            return 400 if ic else 160
        elif place <= 4:
            return 320 if ic else 130
        elif place <= 8:
            return 250 if ic else 100
        elif place <= 16 and competitors >= 48:
            return 200 if ic else 80
        elif place <= 32 and competitors >= 80:
            return 160 if ic else 60
        elif place <= 64 and competitors >= 128:
            return 130 if ic else 50
        elif place <= 128 and competitors >= 256:
            return 100 if ic else 40
        elif place <= 256 and competitors >= 512:
            return 80 if ic else 30
        elif place <= 512 and competitors >= 1024:
            return 60 if ic else 20
        elif place <= 1024 and competitors >= 2046 and ic:
            return 50

    if season == 2025:
        if place == 1:
            return 500 if ic else 350
        elif place == 2 and competitors >= 4:
            return 480 if ic else 325
        elif place <= 4 and competitors >= 8:
            return 420 if ic else 300
        elif place <= 8 and competitors >= 17:
            return 380 if ic else 280
        elif place <= 16 and competitors >= 33:
            return 300 if ic else 160
        elif place <= 32 and competitors >= 65:
            return 200 if ic else 125
        elif place <= 64 and competitors >= 129:
            return 150 if ic else 100
        elif place <= 128 and competitors >= 257:
            return 120 if ic else 80
        elif place <= 256 and competitors >= 513:
            return 100 if ic else 60
        elif place <= 512 and competitors >= 1025:
            return 80 if ic else 40
        elif place <= 1024 and competitors >= 2049:
            return 40 if ic else 20

    if season == 2026:
        if place == 1:
            return 500 if ic else 350
        elif place == 2 and competitors >= 4:
            return 480 if ic else 325
        elif place <= 4 and competitors >= 8:
            return 420 if ic else 300
        elif place <= 8 and competitors >= 17:
            return 380 if ic else 280
        elif place <= 16 and competitors >= 33:
            return 300 if ic else 200
        elif place <= 32 and competitors >= 65:
            return 240 if ic else 160
        elif place <= 64 and competitors >= 129:
            return 180 if ic else 120
        elif place <= 128 and competitors >= 257:
            return 140 if ic else 80
        elif place <= 256 and competitors >= 513:
            return 100 if ic else 60
        elif place <= 512 and competitors >= 1025:
            return 80 if ic else 40
        elif place <= 1024 and competitors >= 2049:
            return 40 if ic else 20

    return 0

"""
get "fancy" round name: Cut, T8 etc
"""
def get_round_name(rnd:str, tour_format:list, players:int = 0) -> str:
    last_swiss = tour_format[0] + tour_format[1]
    if int(rnd) <= last_swiss:
        return rnd

    if players == 2:
        return "Finals"
    if players == 4:
        return "Top 4"
    if players == 8:
        return "Top 8"
    if players == 16:
        return "Top 16"
    if players == 32:
        return "Top 32"

    return "Top Cut"


"""
get a fudged timezone for the event
"""
def _get_event_tz(event_info:dict) -> ZoneInfo:
    tz = None
    if event_info['region'] == 'North America':
        tz = ZoneInfo("America/Chicago")
    elif event_info['region'] == 'Europe':
        tz = ZoneInfo("Europe/Berlin")
    elif event_info['region'] == 'Oceania':
        tz = ZoneInfo("Australia/Sydney")
    elif event_info['region'] == 'Latin America':
        if event_info['country'] == 'Mexico':
            tz = ZoneInfo("America/Mexico_City")
        else:
            tz = ZoneInfo("America/Sao_Paulo")

    return tz


"""
returns if tour is considered "in progress" (ongoing)
"""
def tour_in_progress(event_info:dict, players:bool = False) -> bool:
    if players:
        # check if the tour is actually over (a finalist won)
        for player in players.values():
            for match in player.rounds:
                if match.res != 'W' and match.res != 'L':
                    break
                if match.rname != 'Finals':
                    break
                return False
            break

    # otherwise we'll get rough start times based on best guess timezone
    tz = _get_event_tz(event_info)

    start = datetime.strptime(f"{event_info['start']} 08:00:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
    end = datetime.strptime(f"{event_info['end']} 18:00:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
    now = datetime.now(tz)

    return now >= start and now <= end


"""
only check if we're on/after the start time
"""
def _tour_has_started(event_info:dict) -> bool:
    tz = _get_event_tz(event_info)

    start = datetime.strptime(f"{event_info['start']} 08:00:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
    now = datetime.now(tz)

    return now >= start


"""
only check if we're after the end time
"""
def _tour_has_ended(event_info:dict) -> bool:
    tz = _get_event_tz(event_info)

    end = datetime.strptime(f"{event_info['end']} 18:00:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
    now = datetime.now(tz)

    return now >= end


"""
statuses: complete, upcoming, in_progress
"""
def determine_event_status(event_info:dict) -> str:
    if not event_info['processed']:
        return "upcoming"

    if tour_in_progress(event_info):
        return "in_progress"

    if event_info['processed'] and not _tour_has_started(event_info):
        return "upcoming"

    return "complete"


# some easy helper functions ... notably these are called
# by the usage functions, which parse the data, so they don't
# use the data models, which is why everything is a dict

def player_earned_points(player:dict, points_threshold:int) -> bool:
    if not points_threshold:
        return False
    return player['place'] <= points_threshold


def player_made_phase_two(player:dict, tour_format:list) -> bool:
    if len(player['rounds']) > tour_format[0]:
        return True
    return False


def player_made_cut(player:dict, tour_format:list) -> bool:
    if player['drop'] == -1 and len(player['rounds']) > tour_format[0] + tour_format[1]:
        return True
    return False

