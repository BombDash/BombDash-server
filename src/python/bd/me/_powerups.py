# Copyright (c) 2020 BombDash
from __future__ import annotations

from typing import TYPE_CHECKING

import ba
import bastd.actor.spaz as stdspaz

from ._redefine import redefine_class_methods, redefine_flag, RedefineFlag

if TYPE_CHECKING:
    from typing import Callable, Any, List, Tuple


_callbacks: List[Tuple[str, Any, Callable]] = []


def add_powerup(poweruptype: str, callback: Callable[[ba.PowerupMessage], None], texture: Any) -> None:
    _callbacks.append((poweruptype, texture, callback))


def powerup(poweruptype: str, texture: Any) -> Callable[[Callable], Callable]:
    def decorator(func: Callable) -> Callable:
        add_powerup(poweruptype, func, texture)
        return func

    return decorator


@redefine_class_methods(stdspaz.Spaz)
class Spaz(ba.Actor):
    @redefine_flag(RedefineFlag.DECORATE_AFTER)
    def handlemessage(self, msg: Any, returned: Any = None) -> Any:
        super().handlemessage(msg)
        Spaz.handlemessage(self, msg)
        if isinstance(msg, ba.PowerupMessage):
            for poweruptype, texture, callback in _callbacks:
                if msg.poweruptype == poweruptype:
                    callback(msg)
