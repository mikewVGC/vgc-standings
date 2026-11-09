
from __future__ import annotations

from dataclasses import dataclass

from ops.format_models import (
    Move,
    TeamMember,
    TeamMemberAlt,
)

from lib.formes import (
    get_icon_alt,
    get_mon_alt_from_code,
    get_mon_data_from_code,
)
from lib.moves import get_move_info_from_name
from lib.util import (
    fix_mon_name,
    fix_nature,
    make_item_code,
    make_mon_code,
)


@dataclass
class MonDictMap:
    name:str = "name"
    moves:str = "moves"
    item:str = "item"
    ability:str = "ability"
    tera:str = "tera"
    nature:str = "nature"


def create_team_member_from_mon(mon:dict, key_map:MonDictMap, event_info:dict) -> TeamMember:
    mon_name = fix_mon_name(mon[key_map.name])
    mon_code = make_mon_code(mon_name)
    mon_alt_code = get_icon_alt(mon_code, mon, event_info['rules']['mega'])
    dex_num, types, _, _ = get_mon_data_from_code(mon_code)

    alt_data = None

    alt = get_mon_alt_from_code(mon_code)
    if alt:
        dex_num = alt

    if mon_alt_code:
        alt = get_mon_alt_from_code(mon_alt_code)

    if alt and len(mon_alt_code):
        _, alt_types, alt_name, alt_abilities = get_mon_data_from_code(mon_alt_code)

        if isinstance(alt_abilities, dict):
            alt_abilities = list(alt_abilities.values())

        alt_data = TeamMemberAlt(
            name=alt_name,
            code=mon_alt_code,
            dex=alt,
            types=alt_types,
            ability=alt_abilities[0],
        )
    elif alt:
        dex_num = alt

    mon_item = mon[key_map.item] if len(mon[key_map.item]) else 'No Item'

    moves = [ Move(name=m) for m in mon[key_map.moves] if m ]
    for move in moves:
        _, _, _, move.type = get_move_info_from_name(move.name)
        move.type = move.type.lower()

    return TeamMember(
        name=mon_name,
        code=mon_code,
        dex=dex_num,
        types=types,
        tera=mon.get(key_map.tera, ""),
        nature=fix_nature(mon.get(key_map.nature, "")),
        ability=mon.get(key_map.ability, ""),
        alt=alt_data,
        item=mon_item,
        itemcode=make_item_code(mon_item),
        moves=moves,
    )
