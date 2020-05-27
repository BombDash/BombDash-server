from __future__ import annotations

from typing import TYPE_CHECKING

import random

import ba
from bastd.actor import bomb as stdbomb
from bd.me import bomb, MeBomb, blast
from bd.actor import Portals

if TYPE_CHECKING:
    from typing import Sequence


@bomb('portal_bomb', impact=True)
class PortalBomb(MeBomb):

    def init(self, actor: stdbomb.Bomb, position, velocity, materials):
        factory = stdbomb.get_factory()
        actor.node = ba.newnode('prop', delegate=actor, attrs={
            'body': 'sphere',
            'body_scale': 0.85,
            'position': position,
            'velocity': velocity,
            'materials': materials})

        actor.first_shield = ba.newnode(
            'shield', owner=actor.node, attrs={
                'color': (1, 1, 1),
                'radius': 0.6})

        actor.node.connectattr(
            'position', actor.first_shield, 'position')

        actor.second_shield = ba.newnode(
            'shield', owner=actor.node, attrs={
                'color': (0, 0, 20),
                'radius': 0.4})

        actor.node.connectattr(
            'position', actor.second_shield, 'position')

        color = {
            0: (1, 1, 1),
            1: (20, 0, 0),
            2: (20, 10, 0),
            3: (20, 20, 0),
            4: (0, 20, 0),
            5: (0, 10, 20),
            6: (0, 0, 20),
            7: (10, 0, 20),
            8: (1, 1, 1)
        }

        ba.animate_array(actor.second_shield, 'color',
                         3, color, True)


@blast('portal_bomb')
def portal_blast(self, position, velocity, blast_radius,
                 hit_type, hit_subtype):
    if not self.source_player.node:
        return
    self.node = None
    Portals(
        color=(random.random() * 2,
               random.random() * 2,
               random.random() * 2),
        first_position=position,
        second_position=self.source_player.actor.node.position).autoretain()
    ba.playsound(ba.getsound('laserReverse'), position=position)
