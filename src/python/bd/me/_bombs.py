# Copyright (c) 2020 BombDash
from __future__ import annotations

from typing import TYPE_CHECKING

import random
import ba
from bastd.actor import bomb as stdbomb
from bastd.actor.bomb import BombFactory, ExplodeMessage, get_factory
from ._redefine import redefine_class_methods, redefine_flag, RedefineFlag

if TYPE_CHECKING:
    from typing import Callable, List, Type, Optional, Dict, Sequence, Any

_bombs: List[MeBomb] = []
_blasts: Dict[str, Callable] = {}


def add_bomb(mebomb: MeBomb):
    _bombs.append(mebomb)


def bomb(bomb_type: str, arm_time: float = None, fuse_time: float = None,
         blast_coefficient: float = 1, sticky: bool = False, impact: bool = False,
         is_mine: bool = False):
    def decorator(cls: Type[MeBomb]):
        add_bomb(cls(bomb_type=bomb_type, arm_time=arm_time, fuse_time=fuse_time,
                     blast_coefficient=blast_coefficient, sticky=sticky, impact=impact, is_mine=is_mine))

    return decorator


def add_blast(blast_type: str, callback: Callable):
    _blasts[blast_type] = callback


def blast(blast_type: str):
    def decorator(function: Callable):
        nonlocal blast_type
        add_blast(blast_type, function)

    return decorator


class MeBomb:
    """Class that defines actions and types of bomb

    You must implement this methods in child class:
        init(self, actor, position, velocity, materials) - initialize the bomb (create node, etc)
        arm(self, actor) - for impact-like bombs or mines
        on_impact(self, actor) - handle impact
        on_drop(self, actor) - handle dropped
    """

    def __init__(self, bomb_type: str, arm_time: float = None, fuse_time: float = None,
                 blast_coefficient: float = 1, sticky: bool = False, impact: bool = False,
                 is_mine: bool = False):
        self.bomb_type = bomb_type

        # Functions must be implemented in child class
        # self.init = init
        # self.arm = arm
        # self.on_impact = on_impact
        # self.on_drop = on_drop

        # Settings
        self.arm_time = arm_time
        self.fuse_time = fuse_time
        self.blast_coefficient = blast_coefficient

        # Flags
        self.sticky = sticky
        self.is_impact = impact
        self.is_mine = is_mine

    def init(self, actor, position, velocity, materials):
        pass

    def arm(self, actor):
        pass

    def explode(self, actor):
        pass

    def on_impact(self, actor):
        pass

    def on_drop(self, actor):
        pass

    def handlemessage(self, actor, msg):
        pass


def get_mebomb(bomb_type: str) -> MeBomb:
    for mebomb in _bombs:
        if mebomb.bomb_type == bomb_type:
            return mebomb


@redefine_class_methods(stdbomb.Bomb)
class Bomb(ba.Actor):
    _redefine_methods = ('__init__', '_handle_hit', 'arm', '_handle_impact', '_handle_dropped', 'handlemessage')

    @redefine_flag(RedefineFlag.DECORATE_ADVANCED)
    def __init__(self, old_function: Callable,
                 position=(0.0, 1.0, 0.0),
                 velocity=(0.0, 0.0, 0.0),
                 bomb_type: str = 'normal',
                 blast_radius: float = 2.0,
                 source_player: ba.Player = None,
                 owner: ba.Node = None):
        """Create a new Bomb.

        bomb_type can be standard or one from declared with bd.me.
        Note that for impact or land_mine bombs you have to call arm()
        before they will go off.
        """
        mebomb: MeBomb = get_mebomb(bomb_type)
        if mebomb is None:
            old_function(self, position, velocity, bomb_type, blast_radius, source_player, owner)
            return

        ba.Actor.__init__(self)

        factory = get_factory()
        self.bomb_type = bomb_type
        self._exploded = False
        self.texture_sequence = None
        self.blast_radius = blast_radius

        self._explode_callbacks = []

        # the player this came from
        self.source_player = source_player

        # by default our hit type/subtype is our own, but we pick up types of
        # whoever sets us off so we know what caused a chain reaction
        self.hit_type = 'explosion'
        self.hit_subtype = self.bomb_type

        # if no owner was provided, use an unconnected node ref
        # (nevermind; trying to use None in these type cases instead)
        # if owner is None:
        #     owner = ba.Node(None)

        # the node this came from
        self.owner = owner

        # adding footing-materials to things can screw up jumping and flying
        # since players carrying those things
        # and thus touching footing objects will think they're on solid
        # ground.. perhaps we don't wanna add this even in the tnt case?..
        materials: tuple
        materials = (factory.bomb_material,
                     ba.sharedobj('object_material'))

        if mebomb.is_impact:
            materials = materials + (factory.impact_blast_material,)
        elif mebomb.is_mine:
            materials = materials + (factory.land_mine_no_explode_material,)
        # TODO: add custom materials (now you may add they in mebomb.init)

        fuse_time = None

        mebomb = get_mebomb(self.bomb_type)
        fuse_time = mebomb.fuse_time
        self.blast_radius *= mebomb.blast_coefficient
        if mebomb.sticky:
            materials = materials + (factory.sticky_material,)
        else:
            materials = materials + (factory.normal_sound_material,)
        if mebomb.is_impact:
            materials = materials + (factory.impact_blast_material,)
        if mebomb.is_mine:
            materials = materials + (factory.land_mine_no_explode_material,)
        mebomb.init(self, position, velocity, materials)

        # Light the fuse!!!
        if fuse_time is not None:
            ba.timer(fuse_time,
                     ba.WeakCall(self.handlemessage, ExplodeMessage()))

        ba.animate(self.node, "model_scale", {0: 0, 0.2: 1.3, 0.26: 1})

    @redefine_flag(RedefineFlag.DECORATE_ADVANCED)
    def arm(self, old_function: Callable):
        """Arm the bomb.

        These types of bombs will not explode until they have been armed.
        """
        if not self.node:
            return
        factory = get_factory()
        mebomb: Optional[MeBomb] = get_mebomb(self.bomb_type)
        if mebomb is None:
            old_function(self)
            return
        mebomb.arm(self)
        ba.playsound(factory.activate_sound, 0.5, position=self.node.position)

    @redefine_flag(RedefineFlag.REDEFINE)
    def _handle_hit(self, msg: ba.HitMessage):
        ispunch = (msg.srcnode and msg.srcnode.getnodetype() == 'spaz')

        # Normal bombs are triggered by non-punch impacts;
        # impact-bombs by all impacts.
        mebomb = get_mebomb(self.bomb_type)
        if (not self._exploded and not ispunch
                or (mebomb is not None and (mebomb.is_mine or mebomb.is_impact))):
            # Also lets change the owner of the bomb to whoever is setting
            # us off. (this way points for big chain reactions go to the
            # person causing them).
            if msg._source_player not in [None]:
                self.source_player = msg._source_player

                # Also inherit the hit type (if a landmine sets off by a bomb,
                # the credit should go to the mine)
                # the exception is TNT.  TNT always gets credit.
                if self.bomb_type != 'tnt':
                    self.hit_type = msg.hit_type
                    self.hit_subtype = msg.hit_subtype

            ba.timer(100 + int(random.random() * 100),
                     ba.WeakCall(self.handlemessage, ExplodeMessage()),
                     timeformat=ba.TimeFormat.MILLISECONDS)
        assert self.node
        self.node.handlemessage('impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                                msg.velocity[0], msg.velocity[1],
                                msg.velocity[2], msg.magnitude,
                                msg.velocity_magnitude, msg.radius, 0,
                                msg.velocity[0], msg.velocity[1],
                                msg.velocity[2])

        if msg.srcnode:
            pass

    @redefine_flag(RedefineFlag.DECORATE_ADVANCED)
    def _handle_dropped(self, old_function: Callable):
        mebomb = get_mebomb(self.bomb_type)
        if mebomb is None:
            return old_function(self)
        self.arm_timer = \
            ba.Timer(0.5, ba.WeakCall(self.handlemessage, stdbomb.ArmMessage()))
        mebomb.on_drop(self)

    @redefine_flag(RedefineFlag.DECORATE_ADVANCED)
    def _handle_impact(self, old_function):
        mebomb = get_mebomb(self.bomb_type)
        if mebomb is None:
            old_function(self)
            return
        mebomb.on_impact(self)
        node = ba.getcollision().opposingnode
        # if we're an impact bomb and we came from this node, don't explode...
        # alternately if we're hitting another impact-bomb from the same
        # source, don't explode...
        try:
            node_delegate = node.getdelegate(stdbomb.Bomb)
        except Exception:
            node_delegate = None
        if node:
            if (mebomb.is_impact and
                    (node is self.owner or
                     (isinstance(node_delegate, stdbomb.Bomb)
                      and get_mebomb(node_delegate.bomb_type) is not None
                      and get_mebomb(node_delegate.bomb_type).is_impact
                      and node_delegate.owner is self.owner))):
                return
            self.handlemessage(ExplodeMessage())
    
    @redefine_flag(RedefineFlag.DECORATE_ADVANCED)
    def handlemessage(self, msg: Any, old_function: Callable) -> Any:
        mebomb = get_mebomb(self.bomb_type)
        if not (mebomb is not None and mebomb.handlemessage(self, msg)):
            old_function(self, msg)


@redefine_class_methods(stdbomb.Blast)
class Blast(ba.Actor):
    _redefine_methods = ('__init__',)

    @redefine_flag(RedefineFlag.DECORATE_ADVANCED)
    def __init__(self, old_function: Callable,
                 position: Sequence[float] = (0.0, 1.0, 0.0),
                 velocity: Sequence[float] = (0.0, 0.0, 0.0),
                 blast_radius: float = 2.0,
                 blast_type: str = 'normal',
                 source_player: ba.Player = None,
                 hit_type: str = 'explosion',
                 hit_subtype: str = 'normal'):
        meblast = _blasts.get(blast_type)
        if meblast is None:
            old_function(self, position=position, velocity=velocity, blast_radius=blast_radius,
                         blast_type=blast_type, source_player=source_player, hit_type=hit_type,
                         hit_subtype=hit_subtype)
            return
        """Instantiate with given values."""

        # bah; get off my lawn!
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements

        ba.Actor.__init__(self)

        factory = get_factory()

        self.blast_type = blast_type
        self.source_player = source_player
        self.hit_type = hit_type
        self.hit_subtype = hit_subtype
        self.radius = blast_radius

        # Do we need to light?
        # lcolor = ((0.6, 0.6, 1.0) if self.blast_type == 'ice' else
        #           (1, 0.3, 0.1))
        # light = ba.newnode('light',
        #                    attrs={
        #                        'position': position,
        #                        'volume_intensity_scale': 10.0,
        #                        'color': lcolor
        #                    })

        # scl = random.uniform(0.6, 0.9)
        # scorch_radius = light_radius = self.radius
        # if self.blast_type == 'tnt':
        #     light_radius *= 1.4
        #     scorch_radius *= 1.15
        #     scl *= 3.0
        #
        # iscale = 1.6
        # ba.animate(
        #     light, 'intensity', {
        #         0: 2.0 * iscale,
        #         scl * 0.02: 0.1 * iscale,
        #         scl * 0.025: 0.2 * iscale,
        #         scl * 0.05: 17.0 * iscale,
        #         scl * 0.06: 5.0 * iscale,
        #         scl * 0.08: 4.0 * iscale,
        #         scl * 0.2: 0.6 * iscale,
        #         scl * 2.0: 0.00 * iscale,
        #         scl * 3.0: 0.0
        #     })
        # ba.animate(
        #     light, 'radius', {
        #         0: light_radius * 0.2,
        #         scl * 0.05: light_radius * 0.55,
        #         scl * 0.1: light_radius * 0.3,
        #         scl * 0.3: light_radius * 0.15,
        #         scl * 1.0: light_radius * 0.05
        #     })
        # ba.timer(scl * 3.0, light.delete)

        # make a scorch that fades over time

        # if self.blast_type == 'ice':
        #     ba.playsound(factory.hiss_sound, position=light.position)

        # lpos = light.position
        # ba.playsound(factory.random_explode_sound(), position=lpos)
        # ba.playsound(factory.debris_fall_sound, position=lpos)

        ba.camerashake(intensity=5.0 if self.blast_type == 'tnt' else 1.0)

        _blasts[blast_type](self,
                            position=position,
                            velocity=velocity,
                            blast_radius=blast_radius,
                            hit_type=hit_type,
                            hit_subtype=hit_subtype)
