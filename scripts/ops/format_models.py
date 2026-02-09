
from __future__ import annotations

from dataclasses import dataclass

@dataclass
class TeamMember():
    name: str
    code: str
    altcode: str
    dex: int
    ptype: str
    tera: str
    ability: str
    item: str
    itemcode: str
    moves: list[str] | None = None

@dataclass
class Round():
    round: int
    rname: str
    opp: str
    res: str
    tbl: int
    phase: int
    bye: int = 0
    late: int = 0
    drop: int = 0

@dataclass
class Player():
    name: str
    code: str
    country: str
    place: int
    record: dict[str, int]
    res: dict[str, list | int ]
    cut: bool
    p2: bool
    drop: int
    team: list[TeamMember] | None = None
    rounds: list[Round] | None = None
