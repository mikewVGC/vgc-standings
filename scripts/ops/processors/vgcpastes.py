
from __future__ import annotations
from dataclasses import dataclass

import re

from urllib import request
from urllib.error import URLError, HTTPError

from lib.util import make_code, make_mon_code, make_item_code

from lib.formes import (
    get_mon_data_from_code,
    get_mon_alt_from_code,
    get_icon_alt,
)

from ops.format_models import TeamMember


def process_vgcpastes_teamlist(players, year, code):
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

    for player, paste in player_pastes.items():
        if len(paste) == 0:
            continue
        paste = fetch_paste(paste).splitlines()
        if len(paste):
            players[player].team = parse_paste(paste)

    return True


def fetch_paste(url):
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


def parse_paste(paste):
    mons = []

    paste.append("\n")

    # slightly awkward regexes from the pokepaste source
    main_reg = r"^(?:(.* \()([A-Z][a-z0-9:']+\.?(?:[- ][A-Za-z][a-z0-9:']*\.?)*)(\))|([A-Z][a-z0-9:']+\.?(?:[- ][A-Za-z][a-z0-9:']*\.?)*))(?:( \()([MF])(\)))?(?:( @ )([A-Z][a-z0-9:']*(?:[- ][A-Z][a-z0-9:']*)*))?( *)$"
    move_reg = r"^(-)( ([A-Z][a-z\']*(?:[- ][A-Za-z][a-z\']*)*)(?: \[([A-Z][a-z]+)\])?(?: / [A-Z][a-z\']*(?:[- ][A-Za-z][a-z\']*)*)* *)$"
    stat_reg = r"^(\d+ HP)?( / )?(\d+ Atk)?( / )?(\d+ Def)?( / )?(\d+ SpA)?( / )?(\d+ SpD)?( / )?(\d+ Spe)?( *)$"

    mon = { 'item': '' }
    moves = []
    for line in paste:
        line = line.strip()
        if len(line) == 0:
            if 'species' not in mon:
                continue

            mon_code = make_mon_code(mon['species'])
            dex_num, ptype = get_mon_data_from_code(mon_code)

            alt = get_mon_alt_from_code(mon_code)
            if alt:
                dex_num = alt

            mons.append(TeamMember(
                name=mon['species'],
                code=mon_code,
                altcode=get_icon_alt(mon_code, mon),
                dex=dex_num,
                ptype=ptype.lower(),
                tera=mon['tera'],
                ability=mon['ability'],
                item=mon['item'],
                itemcode=make_item_code(mon['item']),
                moves=moves,
            ))
            mon = {
                'item': ''
            }
            moves = []
            continue

        matches = re.findall(main_reg, line)
        if len(matches):
            if len(matches[0][1]): # species is here if there's a nickname
                mon['species'] = matches[0][1]
            if len(matches[0][8]):
                mon['item'] = matches[0][8]
            if len(matches[0][3]):
                if matches[0][3].startswith("Ability: "):
                    _, mon['ability'] = matches[0][3].split(': ')
                elif matches[0][3].startswith("Tera Type: "):
                    _, mon['tera'] = matches[0][3].split(': ')
                else:
                    mon['species'] = matches[0][3] # if there's no nickname species is here!
        
        matches = re.findall(move_reg, line)
        if len(matches):
            if len(matches[0][2]):
                moves.append(matches[0][2])

        # stats aren't in these pastes, but maybe some day?
        # matches = re.findall(stat_reg, line)

    return mons

        

