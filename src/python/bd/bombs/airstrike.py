from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.actor import bomb as stdbomb
from bd.me import bomb, MeBomb, blast
from bd.actor import Airstrike

if TYPE_CHECKING:
    from typing import Sequence


@bomb('airstrike', impact=True)
class AirstrikeBomb(MeBomb):
    def init(self, actor: stdbomb.Bomb, position, velocity, materials):
        factory = stdbomb.BombFactory.get()
        actor.node = ba.newnode('prop', delegate=actor, attrs={
            'body': 'sphere',
            'model': factory.impact_bomb_model,
            'color_texture': ba.gettexture('ouyaAButton'),
            'position': position,
            'velocity': velocity,
            'shadow_size': 0.3,
            'reflection': 'powerup',
            'reflection_scale': [1.5],
            'materials': materials})


@blast('airstrike')
def airstrike_blast(self: stdbomb.Blast, position, velocity, blast_radius,
                    hit_type, hit_subtype):
    self.node = None  # We must define node
    ba.emitfx(
        position=position,
        velocity=velocity,
        count=75,
        spread=0.7,
        chunk_type='spark')

    Airstrike(position=position, source_player=ba.existing(self._source_player)).autoretain()
    ba.playsound(ba.getsound('laserReverse'))  # position=self.node.position?
