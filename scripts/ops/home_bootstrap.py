
from lib.util import (
    make_season_info_str,
    make_nice_date_str,
    get_season_bookends,
)

def get_home_bootstrap_data(year:int, majors:dict, all_other_seasons:dict) -> dict:
    first_major, last_major, worlds = get_season_bookends(majors)

    recent = list(filter(lambda major: major['status'] == "complete", list(majors.values())))
    upcoming = list(filter(lambda major: major['status'] == "upcoming", list(majors.values())))
    in_progress = list(filter(lambda major: major['status'] == "in_progress", list(majors.values())))

    recent.reverse()
    in_progress.reverse()

    return {
        "currentSeason": year,
        "seasonStatus": make_season_info_str(majors),
        "seasonDates": make_nice_date_str(first_major['start'], last_major['start'], 'through', True),
        "worldsDate": worlds['dates'],
        "recent": recent[0:3],
        "upcoming": upcoming[0:3],
        "inProgress": in_progress,
        "pastSeasons": all_other_seasons,
    }
