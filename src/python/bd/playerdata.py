from __future__ import annotations

from typing import TYPE_CHECKING

from dataclasses import dataclass
from enum import Enum

if TYPE_CHECKING:
    from typing import Optional, Sequence, List


@dataclass
class PrefixData:
    text: str = ""
    speed: int = 0
    animation: Sequence[int] = ()


@dataclass
class ParticleData:
    particle_type: str = 'ice'
    emit_type: str = 'legs'


class Status(Enum):
    ADMIN = 'admin'
    VIP = 'vip'


@dataclass
class PlayerData:
    id: str
    status: str
    prefix: Optional[PrefixData]
    particle: Optional[ParticleData]


_players: List[PlayerData] = []


def add_player(p_data: PlayerData) -> None:
    if p_data in _players:
        del_player(p_data.id)
    _players.append(p_data)


def del_player(p_id) -> None:
    global _players
    _players = [i for i in _players if i.id != p_id]


def get_player(p_id) -> PlayerData:
    try:
        return next(i for i in _players if i.id == p_id)
    except StopIteration:
        pass
