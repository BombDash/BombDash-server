# Copyright (c) 2020 BombDash

import ba
from bastd.actor import powerupbox as bastd_powerupbox
from typing import Sequence, Tuple


def get_powerup_distribution() -> Sequence[Tuple[str, int]]:
    """Set of BombDash server powerups."""
    return (('lucky_block', 3), ('speed', 2), ('jump_boost', 2), ('companion_cube', 2), ('sticky_gift', 2),
            ('portal_bombs', 2), ('elon_mines', 2), ('airstrike_bombs', 2), ('heal_bombs', 1), ('holy_bombs', 1))


def _decorator(f):
    def func(self, *args, **kwargs):
        f(self, *args, **kwargs)
        for powerup, freq in get_powerup_distribution():
            for _i in range(int(freq)):
                self._powerupdist.append(powerup)

        self.tex_speed = ba.gettexture('powerupSpeed')
        self.tex_high_jump = ba.gettexture('buttonJump')
        self.tex_holy_bomb = ba.gettexture('coin')
        self.tex_health_bomb = ba.gettexture('heart')
        self.tex_lucky_block = ba.gettexture('achievementEmpty')
        self.tex_portal_bomb = ba.gettexture('light')
        self.tex_airstrike_bomb = ba.gettexture('menuIcon')
        self.tex_cube_companion = ba.gettexture('landMineLit')
        self.tex_elon_musk_mine = ba.gettexture('achievementMine')
        self.tex_sticky_gift = ba.gettexture('achievementCrossHair')

    return func


bastd_powerupbox.PowerupBoxFactory.__init__ = _decorator(bastd_powerupbox.PowerupBoxFactory.__init__)
