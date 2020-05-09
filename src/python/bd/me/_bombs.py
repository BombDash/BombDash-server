# Copyright (c) 2020 BombDash
from __future__ import annotations

from typing import TYPE_CHECKING

import random
import ba
from bastd.actor import bomb as stdbomb
from bastd.actor.bomb import get_factory, ExplodeMessage
from ._redefine import redefine_class_methods, redefine_flag, RedefineFlag

if TYPE_CHECKING:
    from typing import Callable, List, Type, Optional

_bombs: List[MeBomb] = []


def add_bomb(mebomb: MeBomb):
    _bombs.append(mebomb)


def bomb(bomb_type: str, arm_time: float = None, fuse_time: float = None,
         blast_coefficient: float = 1, sticky: bool = False, impact: bool = False,
         is_mine: bool = False):
    def decorator(cls: Type[MeBomb]):
        add_bomb(cls(bomb_type=bomb_type, arm_time=arm_time, fuse_time=fuse_time,
                     blast_coefficient=blast_coefficient, sticky=sticky, impact=impact, is_mine=is_mine))

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


def get_mebomb(bomb_type: str) -> MeBomb:
    for mebomb in _bombs:
        if mebomb.bomb_type == bomb_type:
            return mebomb


@redefine_class_methods(stdbomb.Bomb)
class Bomb(ba.Actor):
    _redefine_methods = ('__init__', '_handle_hit', 'arm', '_handle_impact', '_handle_dropped')

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
        try:
            old_function(self)
        except AttributeError:
            pass
        else:
            mebomb.on_impact(self)
        self.texture_sequence.connectattr('output_texture', self.node,
                                          'color_texture')
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
            if msg.source_player not in [None]:
                self.source_player = msg.source_player

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
        mebomb.on_drop(self)

    @redefine_flag(RedefineFlag.REDEFINE)
    def _handle_impact(self):
        mebomb = get_mebomb(self.bomb_type)
        node = ba.get_collision_info('opposing_node')
        # if we're an impact bomb and we came from this node, don't explode...
        # alternately if we're hitting another impact-bomb from the same
        # source, don't explode...
        try:
            node_delegate = node.getdelegate()
        except Exception:
            node_delegate = None
        if node:
            if (mebomb is not None and mebomb.is_impact and
                    (node is self.owner or
                     (isinstance(node_delegate, stdbomb.Bomb)
                      and get_mebomb(node_delegate.bomb_type) is not None
                      and get_mebomb(node_delegate.bomb_type).is_impact
                      and node_delegate.owner is self.owner))):
                return
            self.handlemessage(ExplodeMessage())
