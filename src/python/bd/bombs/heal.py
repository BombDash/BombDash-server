# Copyright (c) 2020 BombDash

from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.actor import bomb as stdbomb
from bd.me import bomb, MeBomb, blast
from bd.actor import TreatmentArea

if TYPE_CHECKING:
    from typing import Sequence


# noinspection DuplicatedCode
@bomb('heal', impact=True)
class HealBomb(MeBomb):
    def init(self, actor: stdbomb.Bomb, position, velocity, materials):
        factory = stdbomb.get_factory()
        actor.node = ba.newnode('prop',
                                delegate=actor,
                                attrs={
                                    'position': position,
                                    'velocity': velocity,
                                    'body': 'sphere',
                                    'materials': materials
                                })

        actor.first_shield = ba.newnode(
            'shield', owner=actor.node, attrs={
                'color': (1, 1, 1),
                'radius': 0.6})

        actor.node.connectattr(
            'position', actor.first_shield, 'position')

        actor.second_shield = ba.newnode(
            'shield', owner=actor.node, attrs={
                'color': (20, 0, 0),
                'radius': 0.4})

        actor.node.connectattr(
            'position', actor.second_shield, 'position')

        ba.animate(actor.second_shield, 'radius',
                   {0: 0.1, 0.3: 0.5, 0.6: 0.1}, True)


@blast('heal')
def heal_blast(self: stdbomb.Blast,
               position: Sequence[float] = (0.0, 1.0, 0.0),
               velocity: Sequence[float] = (0.0, 0.0, 0.0),
               blast_radius: float = 2.0,
               hit_type: str = 'explosion',
               hit_subtype: str = 'normal'):
    ba.emitfx(
        position=position,
        velocity=(0, 0, 0),
        count=75,
        spread=0.7,
        chunk_type='spark')

    TreatmentArea(position=position)
    ba.playsound(ba.getsound('healthPowerup'))  # position=?
