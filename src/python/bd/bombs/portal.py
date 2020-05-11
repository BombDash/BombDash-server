from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.actor import bomb as stdbomb
from bd.me import bomb, MeBomb, blast, powerup
from bd.server.actor.portals import Portals

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

        actor.first_shield = bs.newnode(
            'shield', owner=actor.node, attrs={
                'color': (1, 1, 1),
                'radius': 0.6})

        actor.node.connectattr(
            'position', actor.first_shield, 'position')

        actor.second_shield = bs.newnode(
            'shield', owner=actor.node, attrs={
                'color': (0, 0, 20),
                'radius': 0.4})

        actor.node.connectattr(
            'position', actor.second_shield, 'position')

        color = {
            0: (1, 1, 1),
            1000: (20, 0, 0),
            2000: (20, 10, 0),
            3000: (20, 20, 0),
            4000: (0, 20, 0),
            5000: (0, 10, 20),
            6000: (0, 0, 20),
            7000: (10, 0, 20),
            8000: (1, 1, 1)
        }

        bs.animate_array(actor.second_shield, 'color',
                        3, color, True)

@blast('portal_bomb')
def create_portals(self, position, velocity, blast_radius,
                   hit_type, hit_subtype):
    if not self.source_player.node:
        return
    self.node = None
    Portals(
        color=(random.random()*2,
               random.random()*2,
               random.random()*2),
        first_position=position,
        second_position=self.source_player.position).autoretain()
    ba.playsound(ba.getsound('laserReverse'), position=position)

@powerup('portal_bombs', 'light', freq=1, bomb_type='portal_bomb')
def portal_bombs_callback(self: stdspaz.Spaz, msg: ba.PowerupMessage):
    self.inc_bomb_count('portal_bomb')