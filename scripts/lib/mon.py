
from __future__ import annotations

from dataclasses import dataclass

from ops.format_models import (
    Move,
    TeamMember,
)

from lib.formes import (
    get_icon_alt,
    get_mon_alt_from_code,
    get_mon_data_from_code,
    get_mon_name_from_code,
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
    mon_alt_name = mon_name
    mon_code = make_mon_code(mon_name)
    mon_alt_code = get_icon_alt(mon_code, mon, event_info['rules']['mega'])
    dex_num, ptype, stype, _ = get_mon_data_from_code(mon_code)

    alt = get_mon_alt_from_code(mon_alt_code) if mon_alt_code else get_mon_alt_from_code(mon_code)
    if alt:
        dex_num = alt
        mon_alt_name = get_mon_name_from_code(mon_alt_code)

    mon_item = mon[key_map.item] if len(mon[key_map.item]) else 'No Item'

    moves = [ Move(name=m) for m in mon[key_map.moves] if m ]
    for move in moves:
        _, _, _, move.type = get_move_info_from_name(move.name)
        move.type = move.type.lower()

    return TeamMember(
        name=mon_name,
        code=mon_code,
        altname=mon_alt_name,
        altcode=mon_alt_code,
        dex=dex_num,
        ptype=ptype.lower(),
        stype=stype.lower(),
        tera=mon.get(key_map.tera, ""),
        nature=fix_nature(mon.get(key_map.nature, "")),
        ability=mon.get(key_map.ability, ""),
        item=mon_item,
        itemcode=make_item_code(mon_item),
        moves=moves,
    )
