# Copyright (c) 2020 BombDash
from __future__ import annotations

from typing import TYPE_CHECKING

import ba
import _ba
import bastd.actor.spaz as stdspaz
from bastd.actor import powerupbox
from bastd.actor.powerupbox import get_factory, DEFAULT_POWERUP_INTERVAL

from ._redefine import redefine_class_methods, redefine_flag, RedefineFlag

if TYPE_CHECKING:
    from typing import Callable, Any, List, Tuple, Sequence, Dict


_callbacks: List[Tuple[str, Any, Callable]] = []
_powerupdist: List[Tuple[str, int]] = []
_poweruptextures: Dict[str, str] = {}


def add_powerup(poweruptype: str, callback: Callable[[ba.PowerupMessage], None], texture: str, freq: int) -> None:
    _callbacks.append((poweruptype, texture, callback))
    _powerupdist.append((poweruptype, freq))
    _poweruptextures[poweruptype] = texture


def powerup(poweruptype: str, texture: str, freq: int) -> Callable[[Callable], Callable]:
    def decorator(func: Callable) -> Callable:
        add_powerup(poweruptype, func, texture, freq)
        return func

    return decorator


@redefine_class_methods(stdspaz.Spaz)
class Spaz(ba.Actor):
    _redefine_methods = ('handlemessage',)

    @redefine_flag(RedefineFlag.DECORATE_AFTER)
    def handlemessage(self, msg: Any, returned: Any = None) -> Any:
        super(stdspaz.Spaz, self).handlemessage(msg)
        if isinstance(msg, ba.PowerupMessage):
            for poweruptype, texture, callback in _callbacks:
                if msg.poweruptype == poweruptype:
                    callback(self, msg)


@redefine_class_methods(powerupbox.PowerupBoxFactory)
class PowerupBoxFactory:
    _redefine_methods = ('__init__',)

    @redefine_flag(RedefineFlag.DECORATE_AFTER)
    def __init__(self, returned: Any = None) -> None:
        for poweruptype, freq in _powerupdist:
            for _i in range(int(freq)):
                self._powerupdist.append(poweruptype)


@redefine_class_methods(powerupbox.PowerupBox)
class PowerupBox(ba.Actor):
    _redefine_methods = ('__init__',)

    def __init__(self,
                 position: Sequence[float] = (0.0, 1.0, 0.0),
                 poweruptype: str = 'triple_bombs',
                 expire: bool = True):
        """Create a powerup-box of the requested type at the given position.

        see ba.Powerup.poweruptype for valid type strings.
        """

        super(powerupbox.PowerupBox, self).__init__()

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
        else:
            if poweruptype in _poweruptextures:
                tex = ba.gettexture(_poweruptextures[poweruptype])
            else:
                raise Exception('invalid poweruptype: ' + str(poweruptype))

        if len(position) != 3:
            raise Exception('expected 3 floats for position')

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
        curve = ba.animate(self.node, 'model_scale', {0: 0, 0.14: 1.6, 0.2: 1})
        ba.timer(0.2, curve.delete)

        if expire:
            ba.timer(DEFAULT_POWERUP_INTERVAL - 2.5,
                     ba.WeakCall(self._start_flashing))
            ba.timer(DEFAULT_POWERUP_INTERVAL - 1.0,
                     ba.WeakCall(self.handlemessage, ba.DieMessage()))
