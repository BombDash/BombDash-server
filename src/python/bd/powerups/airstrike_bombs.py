# Copyright (c) 2020 BombDash
from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bd.me import powerup

if TYPE_CHECKING:
    from typing import Any


@powerup('airstrike_bombs', 'тут должна быть текстура')
def airstrike_bombs_callback(msg: ba.PowerupMessage) -> None:
    print('powerup accepted')
