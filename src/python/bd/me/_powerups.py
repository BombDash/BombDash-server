# Copyright (c) 2020 BombDash

from typing import TYPE_CHECKING

import ba
import bastd.actor.spaz as stdspaz

from ._redefine import redefine_class_methods, redefine_flag, RedefineFlag

if TYPE_CHECKING:
    from typing import Callable, Any, List, Tuple


callbacks: List[Tuple[str, Callable]] = []


def add_powerup(poweruptype: str, callback: Callable[[ba.PowerupMessage], None]) -> None:
    callbacks.append((poweruptype, callback))


@redefine_class_methods(stdspaz.Spaz)
class Spaz(ba.Actor):
    @redefine_flag(RedefineFlag.DECORATE_AFTER)
    def handlemessage(self, msg: Any, returned: Any = None) -> Any:
        super().handlemessage(msg)
        Spaz.handlemessage(self, msg)
        if isinstance(msg, ba.PowerupMessage):
            for poweruptype, callback in callbacks:
                if msg.poweruptype == poweruptype:
                    callback(msg)
