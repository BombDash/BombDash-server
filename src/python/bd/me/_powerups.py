# Copyright (c) 2020 BombDash
from __future__ import annotations

from typing import TYPE_CHECKING

import ba
import bastd.actor.spaz as stdspaz
import bastd.actor.bomb as stdbomb
from bastd.actor.popuptext import PopupText
from bastd.gameutils import SharedObjects
from bastd.actor import powerupbox
from bastd.actor.powerupbox import DEFAULT_POWERUP_INTERVAL
from bd.locale import get_locale  # Хмм, ну бывает, ну me же часть bd, почему бы и нет (ну не бейте пж)

from ._redefine import redefine_class_methods, redefine_flag, RedefineFlag

if TYPE_CHECKING:
    from typing import Callable, Any, List, Tuple, Sequence, Dict, Optional

_callbacks: List[Tuple[str, Any, Callable]] = []
_powerupdist: List[Tuple[str, int]] = []
_poweruptextures: Dict[str, str] = {}
_bombtextures: Dict[str, str] = {}


def add_powerup(poweruptype: str, callback: Callable[[ba.PowerupMessage], None],
                texture: str, freq: int, bomb_type: Optional[str] = None) -> None:
    _callbacks.append((poweruptype, texture, callback))
    _powerupdist.append((poweruptype, freq))
    _poweruptextures[poweruptype] = texture
    if bomb_type is not None:
        _bombtextures[bomb_type] = texture


def powerup(poweruptype: str, texture: str, freq: int,
            bomb_type: Optional[str] = None) -> Callable[[Callable], Callable]:
    def decorator(func: Callable) -> Callable:
        add_powerup(poweruptype, func, texture, freq, bomb_type)
        return func

    return decorator


@redefine_class_methods(stdspaz.Spaz)
class Spaz(ba.Actor):
    _redefine_methods = ('handlemessage', 'inc_bomb_count',
                         'dec_bomb_count', 'drop_bomb', 'init_bomb_count')

    @redefine_flag(RedefineFlag.DECORATE_AFTER)
    def handlemessage(self, msg: Any, returned: Any = None) -> Any:
        super(stdspaz.Spaz, self).handlemessage(msg)
        if isinstance(msg, ba.PowerupMessage):
            if not self.is_alive():
                return
            for poweruptype, texture, callback in _callbacks:
                if msg.poweruptype == poweruptype:
                    if ba.app.config.get('Powerup Popups', True):
                        powerup_text = get_locale(
                            'powerup_names')[poweruptype]

                        PopupText(
                            ba.Lstr(translate=('gameDescriptions',
                                               powerup_text)),
                            color=(1, 1, 1),
                            scale=1,
                            position=self.node.position).autoretain()
                    callback(self, msg)

    @redefine_flag(RedefineFlag.REDEFINE)
    def inc_bomb_count(self, bomb_type):
        if not hasattr(self, 'exbomb_count'):
            self.exbomb_count = {}
        count = self.exbomb_count.get(bomb_type, 0) + 1
        self.exbomb_count[bomb_type] = count if count > 0 else 0
        if self.exbomb_count[bomb_type] != 0:
            self.node.counter_text = 'x' + str(self.exbomb_count[bomb_type])
            self.node.counter_texture = ba.gettexture(_bombtextures[bomb_type])
        else:
            self.node.counter_text = ''

    def init_bomb_count(self):  # FIXME redefine init or add automated init
        if not hasattr(self, 'exbomb_count'):
            self.exbomb_count = {}

    @redefine_flag(RedefineFlag.REDEFINE)
    def dec_bomb_count(self, bomb_type):
        if not hasattr(self, 'exbomb_count'):
            self.exbomb_count = {}
        count = self.exbomb_count.get(bomb_type, 0) - 1
        self.exbomb_count[bomb_type] = count if count > 0 else 0
        if self.exbomb_count[bomb_type] != 0:  # TODO: cleanup this
            self.node.counter_text = 'x' + str(self.exbomb_count[bomb_type])
            self.node.counter_texture = ba.gettexture(_bombtextures[bomb_type])
        else:
            self.node.counter_text = ''

    @redefine_flag(RedefineFlag.REDEFINE)
    def drop_bomb(self):
        """
        Tell the spaz to drop one of his bombs, and returns
        the resulting bomb object.
        If the spaz has no bombs or is otherwise unable to
        drop a bomb, returns None.
        """

        if (self.land_mine_count <= 0 and self.bomb_count <= 0 and not any(
                self.exbomb_count.values())) or self.frozen:
            return None
        assert self.node
        pos = self.node.position_forward
        vel = self.node.velocity
        bomb_type: str
        dropping_bomb: bool

        if self.land_mine_count > 0:
            dropping_bomb = False
            self.set_land_mine_count(self.land_mine_count - 1)
            bomb_type = 'land_mine'
        else:
            self.init_bomb_count()
            for exbomb_type in self.exbomb_count:
                if self.exbomb_count[exbomb_type] > 0:
                    self.dec_bomb_count(exbomb_type)
                    bomb_type = exbomb_type
                    dropping_bomb = False
                    break
            else:
                dropping_bomb = True
                bomb_type = self.bomb_type

        bomb = stdbomb.Bomb(position=(pos[0], pos[1] - 0.0, pos[2]),
                            velocity=(vel[0], vel[1], vel[2]),
                            bomb_type=bomb_type,
                            blast_radius=self.blast_radius,
                            source_player=self.source_player,
                            owner=self.node).autoretain()

        assert bomb.node
        if dropping_bomb:
            self.bomb_count -= 1
            bomb.node.add_death_action(
                ba.WeakCall(self.handlemessage, stdspaz.BombDiedMessage()))
        self._pick_up(bomb.node)

        for clb in self._dropped_bomb_callbacks:
            clb(self, bomb)

        return bomb


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

        factory = powerupbox.PowerupBoxFactory.get()
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
                              SharedObjects.get().object_material)
            })  # yapf: disable

        # Animate in.
        curve = ba.animate(self.node, 'model_scale', {0: 0, 0.14: 1.6, 0.2: 1})
        ba.timer(0.2, curve.delete)

        if expire:
            ba.timer(DEFAULT_POWERUP_INTERVAL - 2.5,
                     ba.WeakCall(self._start_flashing))
            ba.timer(DEFAULT_POWERUP_INTERVAL - 1.0,
                     ba.WeakCall(self.handlemessage, ba.DieMessage()))
