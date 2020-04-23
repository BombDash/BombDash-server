# Copyright (c) 2020 BombDash

from bastd.actor import powerupbox as bastd_powerupbox
from typing import Sequence, Tuple


def get_powerup_distribution() -> Sequence[Tuple[str, int]]:
    """Set of BombDash server powerups."""
    return (('lucky_block', 3), ('speed', 2), ('jump_boost', 2), ('companion_cube', 2), ('sticky_gift', 2),
            ('portal_bombs', 2), ('elon_mines', 2), ('airstrike_bombs', 2), ('heal_bombs', 1), ('holy_bombs', 1))


def add_bd_powerups(f):
    def func(self, *args, **kwargs):
        f(self, *args, **kwargs)
        for powerup, freq in get_powerup_distribution():
            for _i in range(int(freq)):
                self._powerupdist.append(powerup)

    return func


bastd_powerupbox.PowerupBoxFactory.__init__ = add_bd_powerups(bastd_powerupbox.PowerupBoxFactory.__init__)
