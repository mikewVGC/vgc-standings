
from __future__ import annotations

import re

from urllib import request
from urllib.error import URLError, HTTPError
from dataclasses import asdict

from paste_parser.paste_parser import PasteParser

from lib.util import make_code, make_mon_code, make_item_code

from lib.formes import (
    get_mon_data_from_code,
    get_mon_alt_from_code,
    get_icon_alt,
)

from lib.moves import get_move_info_from_name

from lib.mon import (
    create_team_member_from_mon,
    MonDictMap,
)

from ops.format_models import (
    TeamMember,
    Move,
)


def process_vgcpastes_teamlist(players:dict, event_info:dict, year:int, code:str) -> bool:
    player_pastes = {}
    try:
        with open(f"data/majors/{year}/{code}-teams.txt", encoding='utf8') as file:
            lines = file.read().splitlines()
            for i, line in enumerate(lines):
                player, paste = line.split('=')
                player_code = make_code(player)

                if player_code not in players:
                    print(f"[{code}] {player} ({player_code}) not found in main in player list")
                    continue

                player_pastes[player_code] = paste

    except FileNotFoundError:
        return False

    mon_map = MonDictMap(name="species")

    for player, paste in player_pastes.items():
        if len(paste) == 0:
            continue
        paste = fetch_paste(paste)
        if len(paste):
            players[player].team = parse_paste(paste, event_info, mon_map)

    return True


def fetch_paste(url:str) -> str:
    cache = "data/pastes"
    paste_id = url.rsplit('/', 1)[-1]
    try:
        with open(f"{cache}/{paste_id}") as paste:
            return paste.read()
    except FileNotFoundError:
        ...

    print(f"-- Downloading paste {paste_id}")
    data = ""
    try:
        with request.urlopen(f"{url}/raw") as resp:
            data = resp.read().decode('utf-8')
            with open(f"{cache}/{paste_id}", 'w') as paste:
                paste.write(data)
    except HTTPError as e:
        print(f"HTTPError downloading paste {url}: [{e.code}] {e.reason}")
    except URLError as e:
        print(f"URLError downloading paste {url}: {e.reason}")

    return data


def parse_paste(paste:str, event_info:dict, mon_map:MonDictMap) -> list:
    parser = PasteParser()

    parsed_mons = parser.parse(paste)

    mons = []

    for mon in parsed_mons:
        mons.append(
            create_team_member_from_mon(asdict(mon), mon_map, event_info)
        )

    return mons

        

