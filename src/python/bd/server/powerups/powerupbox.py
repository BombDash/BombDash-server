# Copyright (c) 2020 BombDash

import ba
import bastd.actor.powerupbox as bastd_powerupbox
from typing import Sequence
from bastd.actor.powerupbox import DEFAULT_POWERUP_INTERVAL, get_factory


def _decorator_powerupbox(f):
    def func(self,
             position: Sequence[float] = (0.0, 1.0, 0.0),
             poweruptype: str = 'triple_bombs',
             expire: bool = True):
        """Create a powerup-box of the requested type at the given position.

        see ba.Powerup.poweruptype for valid type strings.
        """

        # __class__ = self.__class__  # Fuck it
        ba.Actor.__init__(self)

        factory = get_factory()
        self.poweruptype = poweruptype
        self._powersgiven = False

        if poweruptype == 'triple_bombs':
            tex = factory.tex_bomb
        elif poweruptype == 'punch':
            tex = factory.tex_punch
        elif poweruptype == 'ice_bombs':
            tex = factory.tex_ice_bombs
        elif poweruptype == 'impact_bombs':
            tex = factory.tex_impact_bombs
        elif poweruptype == 'land_mines':
            tex = factory.tex_land_mines
        elif poweruptype == 'sticky_bombs':
            tex = factory.tex_sticky_bombs
        elif poweruptype == 'shield':
            tex = factory.tex_shield
        elif poweruptype == 'health':
            tex = factory.tex_health
        elif poweruptype == 'curse':
            tex = factory.tex_curse

        # BombDash server powerups
        elif poweruptype == 'speed':
            tex = factory.tex_speed
            light_color = (0.0, 1.0, 0.0)
        elif poweruptype == 'jump_boost':
            tex = factory.tex_high_jump
            light_color = (1.0, 1.0, 1.0)
        elif poweruptype == 'companion_cube':
            tex = factory.tex_cube_companion
            light_color = (0.0, 1.0, 0.0)
        elif poweruptype == 'holy_bombs':
            tex = factory.tex_holy_bomb
            light_color = (1.0, 0.6, 0.0)
        elif poweruptype == 'elon_mines':
            tex = factory.tex_elon_musk_mine
            light_color = (1.0, 1.0, 1.0)
        elif poweruptype == 'airstrike_bombs':
            tex = factory.tex_airstrike_bomb
            light_color = (1.0, 1.0, 1.0)
        elif poweruptype == 'portal_bombs':
            tex = factory.tex_portal_bomb
            light_color = (0.5, 0.1, 1.0)
        elif poweruptype == 'heal_bombs':
            tex = factory.tex_health_bomb
            light_color = (1.0, 1.0, 1.0)
        elif poweruptype == 'sticky_gift':
            tex = factory.tex_sticky_gift
            light_color = (1.0, 1.0, 1.0)
        elif poweruptype == 'lucky_block':
            tex = factory.tex_lucky_block
            light_color = (1.0, 1.0, 0.0)

        else:
            raise Exception("invalid poweruptype: " + str(poweruptype))

        if len(position) != 3:
            raise Exception("expected 3 floats for position")

        self.node = ba.newnode(
            'prop',
            delegate=self,
            attrs={
                'body': 'box',
                'position': position,
                'model': factory.model,
                'light_model': factory.model_simple,
                'shadow_size': 0.5,
                'color_texture': tex,
                'reflection': 'powerup',
                'reflection_scale': [1.0],
                'materials': (factory.powerup_material,
                              ba.sharedobj('object_material'))
            })  # yapf: disable

        # Animate in.
        curve = ba.animate(self.node, "model_scale", {0: 0, 0.14: 1.6, 0.2: 1})
        ba.timer(0.2, curve.delete)

        if expire:
            ba.timer(DEFAULT_POWERUP_INTERVAL - 2.5,
                     ba.WeakCall(self._start_flashing))
            ba.timer(DEFAULT_POWERUP_INTERVAL - 1.0,
                     ba.WeakCall(self.handlemessage, ba.DieMessage()))

    return func


bastd_powerupbox.PowerupBox.__init__ = _decorator_powerupbox(bastd_powerupbox.PowerupBox.__init__)
