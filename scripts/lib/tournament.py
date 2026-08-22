from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from dataclasses import asdict

from lib.limitless import determine_tournament_structure as limitless_determine_tournament_structure
from lib.vr import determine_tournament_structure as vr_determine_tournament_structure

from ops.format_models import Player

from lib.tourlib import(
    structure2023,
    structure2024,
    structure2025,
    structure2026,
    structure2027,

    points2023,
    points2024,
    points2025,
    points2026,
    points2027,
)

from constants import (
    DT_LIMITLESS,
    DT_VICTORYROAD,
)

"""
returns (day 1 rounds, day 2 rounds, top cut min)
I don't think anything actually uses the third value yet?
"""
def get_tournament_structure(season:int, competitors:int, event_info:dict, data_type:str) -> tuple | None:
    if season == "grassroots":
        if data_type == DT_LIMITLESS:
            return limitless_determine_tournament_structure(season, competitors, event_info)
        elif data_type == DT_VICTORYROAD:
            return vr_determine_tournament_structure(season, competitors, event_info)

    if season == 2023:
        return structure2023.get_tournament_structure(competitors, event_info)
    elif season == 2024:
        return structure2024.get_tournament_structure(competitors, event_info)
    elif season == 2025:
        return structure2025.get_tournament_structure(competitors, event_info)
    elif season == 2026:
        return structure2026.get_tournament_structure(competitors, event_info)
    elif season == 2027:
        return structure2027.get_tournament_structure(competitors, event_info)

    return None


"""
given a number of competitors, return how many will earn points
"""
def get_points_threshold(season:int, competitors:int) -> int | None:
    if season == "limitless":
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

    if season == 2023:
        return points2023.get_points_threshold(competitors)
    elif season == 2024:
        return points2024.get_points_threshold(competitors)
    elif season == 2025:
        return points2025.get_points_threshold(competitors)
    elif season == 2026:
        return points2026.get_points_threshold(competitors)
    elif season == 2027:
        return points2027.get_points_threshold(competitors)

    return None

"""
Get the champ points a player earned based on # of competitors and placement
"""
def get_points_earned(season:int, competitors:int, place:int, ic:bool = False) -> int | None:
    # below the threshold let's just not bother
    if place > get_points_threshold(season, competitors):
        return 0

    if season == 2023:
        return points2023.get_points_earned(competitors, place, ic)
    elif season == 2024:
        return points2024.get_points_earned(competitors, place, ic)
    elif season == 2025:
        return points2025.get_points_earned(competitors, place, ic)
    elif season == 2026:
        return points2026.get_points_earned(competitors, place, ic)
    elif season == 2027:
        return points2027.get_points_earned(competitors, place, ic)

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
    if 'tz' in event_info:
        tz = ZoneInfo(event_info['tz'])
    elif event_info['region'] == 'North America':
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
def tour_in_progress(event_info:dict, players:dict = False) -> bool:
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
def determine_event_status(event_info:dict, players:dict = False) -> str:
    if not event_info['processed']:
        return "upcoming"

    if tour_in_progress(event_info, players):
        return "in_progress"

    if event_info['processed'] and not _tour_has_started(event_info):
        return "upcoming"

    return "complete"


"""
determines if the player made phase 2... can take Player or dict,
but the dict needs to be compatible with Player
"""
def player_made_phase_two(player:dict|Player, tour_format:list) -> bool:
    pl = player
    if type(pl) is Player:
        pl = asdict(player)

    # simple check for after day 2 has begun
    if len(pl['rounds']) > tour_format[0]:
        return True

    # lazy check for after phase 1 has completed
    if (
        len(pl['rounds']) == tour_format[0] and
        tour_format[1] > 0 and
        pl['record']['l'] <= 2
    ):
        return True

    return False


# some easy helper functions ... notably these are called
# by the usage functions, which parse the data, so they don't
# use the data models, which is why everything is a dict

def player_earned_points(player:dict, points_threshold:int) -> bool:
    if not points_threshold:
        return False
    return player['place'] <= points_threshold


def player_made_cut(player:dict, tour_format:list) -> bool:
    if player['drop'] == -1 and len(player['rounds']) > tour_format[0] + tour_format[1]:
        return True
    return False
