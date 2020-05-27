from __future__ import annotations

from typing import TYPE_CHECKING, Any

import ba
from bastd.actor import bomb as stdbomb
from bd.me import bomb, MeBomb
from bd.actor import AutoAim

if TYPE_CHECKING:
    from typing import Sequence, Union


class SetStickyMessage:
    pass


class StickyGiftFactory:
    @classmethod
    def get(cls) -> StickyGiftFactory:
        activity = ba.getactivity()
        factory: cls
        try:
            factory = activity.shared_sticky_gift_factory
        except AttributeError:
            factory = activity.shared_sticky_gift_factory = cls()
        assert isinstance(factory, cls)
        return factory

    def __init__(self):
        bomb_factory = stdbomb.get_factory()
        self.sticky_gift_material = ba.Material()
        self.sticky_gift_material.add_actions(
            conditions=(
                ('we_are_older_than', 200), 'and',
                ('they_are_older_than', 200), 'and',
                ('eval_colliding',), 'and',
                (('they_dont_have_material', bomb_factory.land_mine_no_explode_material), 'and',
                 (('they_have_material', ba.sharedobj('object_material')), 'or',
                  ('they_have_material', ba.sharedobj('player_material'))))),
            actions=(
                ('message', 'our_node',
                 'at_connect', SetStickyMessage())))
        self.sticky_gift_texture = ba.gettexture('egg2')
        self.sticky_gift_model = bomb_factory.sticky_bomb_model


@bomb("sticky_gift", blast_coefficient=0.3)
class StickyGift(MeBomb):
    def init(self, actor: stdbomb.Bomb, position: Sequence[Union[int, float]],
             velocity: Sequence[Union[int, float]], materials: Sequence[ba.Material]):
        factory = StickyGiftFactory.get()
        materials += (factory.sticky_gift_material,)
        actor.node = ba.newnode('prop', delegate=actor, attrs={
            'body': 'sphere',
            'model': factory.sticky_gift_model,
            'light_model': factory.sticky_gift_model,
            'color_texture': factory.sticky_gift_texture,
            'position': position,
            'velocity': velocity,
            'shadow_size': 0.44,
            'reflection': 'powerup',
            'reflection_scale': [1],
            'materials': materials})

    def on_drop(self, actor: stdbomb.Bomb):
        actor.arm_timer = ba.Timer(0.25, ba.WeakCall(actor.handlemessage, stdbomb.ArmMessage()))

    def arm(self, actor: stdbomb.Bomb):
        ba.playsound(ba.getsound('activateBeep'),
                     position=actor.node.position)

        actor.aim = AutoAim(actor.node, actor.owner)

    def handlemessage(self, actor: stdbomb.Bomb, msg: Any) -> bool:
        if isinstance(msg, ba.PickedUpMessage):
            if actor.node and actor.owner != msg.node:
                ba.playsound(ba.getsound("corkPop"),
                             position=actor.node.position)

                actor.explode()
                return True
        elif isinstance(msg, SetStickyMessage):
            node = ba.getcollision().opposingnode
            self.on_sticky_gift(actor, node)
            return True
        return False

    @staticmethod
    def on_sticky_gift(actor: stdbomb.Bomb, node: ba.Node) -> None:
        if (actor.node and node is not actor.owner and
                ba.sharedobj('player_material') in node.materials):
            actor.node.sticky = True

            def wrapper():
                if actor.node:
                    actor.node.extra_acceleration = (0, 80, 0)

                if hasattr(actor, 'aim') and actor.aim:
                    assert isinstance(actor.aim, AutoAim)
                    actor.aim.off()

            ba.timer(0.01, wrapper)
