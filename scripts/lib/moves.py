from __future__ import annotations

import json

from lib.util import make_move_code

movedex = {}
with open("data/common/moves.json") as file:
    movedex = json.loads(file.read())


# return bp, accuracy, category, type
def get_move_info_from_name(move_name:str) -> (int, int, str, str):
    move_code = make_move_code(move_name)

    if move_code not in movedex:
        print(f"Move '{move_name}' not found in movedex")
        return 0, 0, '', ''

    move = movedex[move_code]
    return move['basePower'], move['accuracy'], move['category'], move['type']
