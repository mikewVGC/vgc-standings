
import re

from lib.tournament import player_made_phase_two

from lib.util import (
    make_code,
    fix_mon_name,
    make_mon_code,
    make_item_code,
)

from lib.formes import (
    get_mon_data_from_code,
    get_mon_alt_from_code,
    get_icon_alt,
)

from ops.format_models import (
    TeamMember,
    Round,
    Player,
)

"""
process limitless api... this is the easiest one
"""
def process_limitless_event(data:list, tour_format:list, official_order:list) -> (list, int, dict):
    return players, phase_two_count, players_in_cut_round
