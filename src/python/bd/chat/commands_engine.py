from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from _ba import chatmessage, get_foreground_host_activity
from datetime import datetime
from bd.playerdata import Status, get_player_by, PlayerData
from dataclasses import dataclass
from bd.locale import get_locale

if TYPE_CHECKING:
    from typing import Callable, Dict, List, Sequence


@dataclass
class Command:
    commands: Sequence[str]  # Without /
    statuses: Dict[Status, int]  # minimal interval in seconds
    callback: Callable[[PlayerData, List[str]], type(None)]


_handlers: List[Command] = []
_lastrun: Dict[str, Dict[str, int]] = {}  # Latest command run Dict[player_id, Dict[command, ba.time]]


def _notify_handlers(cmd: str, playerdata: PlayerData):
    args = cmd.split()
    for handler in _handlers:
        if args[0] in handler.commands and playerdata.status in handler.statuses:
            if _lastrun.get(playerdata.id, {}).get(args[0], 0) + handler.statuses[
                    playerdata.status] < int(datetime.now().timestamp()):
                try:
                    with ba.Context(get_foreground_host_activity()):
                        handler.callback(playerdata, args)
                except Exception:
                    ba.print_exception(f'Error while processing command {cmd} from {playerdata.id}')
                    chatmessage(get_locale('command_some_error'))
                lastrun = _lastrun.get(playerdata.id, {})
                lastrun[args[0]] = int(datetime.now().timestamp())
                _lastrun[playerdata.id] = lastrun
            else:
                chatmessage(get_locale('commands_too_many'))


def process_command(client_id: int, cmd: str):
    if client_id == -1:
        return False
    if cmd.startswith('/'):
        p_data = get_player_by('client_id', client_id)
        if p_data:
            _notify_handlers(cmd[1:], playerdata=p_data)
        return True  # it is command
    return False


def servercommand(commands: Sequence[str], statuses: Dict[Status, int]):
    def decorator(func: Callable[[PlayerData], type(None)]):
        _handlers.append(Command(
            commands=commands,
            statuses=statuses,
            callback=func
        ))
        return func

    return decorator
