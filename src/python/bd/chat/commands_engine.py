from __future__ import annotations

from typing import TYPE_CHECKING

from dataclasses import dataclass
from enum import Enum
import ba
from ba import _hooks as bahooks

if TYPE_CHECKING:
    from typing import Callable, Sequence, Dict, Tuple


class Permissions(Enum):
    ROOT = 0
    BAN = 1
    KICK = 2
    KILL = 3
    AFFECT_PLAYERS = 4


@dataclass
class Privilege:
    # frequency - maximum possible <(1)> permission commands in <(2)> seconds.
    max_freq: Dict[Permissions, Tuple[int, int]]
    total_freq: Tuple[int, int]


@dataclass
class Command:
    privileges: Sequence[Privilege]


def process_command(client_id: int, cmd: str):
    ba.screenmessage(f'executing command {cmd}')


# Note: now this hook isn't work
def filter_chat_message_decorator(func: Callable) -> Callable:
    def filter_chat_message(msg: str, client_id: int):
        func(client_id, msg)
        if msg.startswith('/'):
            process_command(client_id, msg[1:])
            return None
    return filter_chat_message


bahooks.filter_chat_message = filter_chat_message_decorator(bahooks.filter_chat_message)
