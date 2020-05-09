# Copyright (c) 2020 BombDash

import ba
from bastd.actor import bomb as stdbomb
from bd.me import bomb, MeBomb


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
