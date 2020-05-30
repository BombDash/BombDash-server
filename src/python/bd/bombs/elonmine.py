from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.actor import bomb as stdbomb
from bd.me import bomb, MeBomb, blast
from bd.actor import AutoAim

if TYPE_CHECKING:
    from typing import Sequence, Union


@bomb('elon_mine', is_mine=True, blast_coefficient=0.7, arm_time=0.5)
class ElonMine(MeBomb):
    def init(self, actor: stdbomb.Bomb, position: Sequence[Union[int, float]],
             velocity: Sequence[Union[int, float]], materials: Sequence[ba.Material]):
        factory = stdbomb.BombFactory.get()
        actor.node = ba.newnode('prop', delegate=actor, attrs={
            'body': 'landMine',
            'model': factory.land_mine_model,
            'light_model': factory.land_mine_model,
            'color_texture': ba.gettexture('achievementCrossHair'),
            'position': position,
            'velocity': velocity,
            'shadow_size': 0.44,
            'reflection': 'powerup',
            'reflection_scale': [1],
            'materials': materials})

    def arm(self, actor: stdbomb.Bomb):
        factory = stdbomb.get_factory()
        elon_mine_lit_tex = ba.gettexture('circleNoAlpha')
        elon_mine_tex = ba.gettexture('achievementCrossHair')
        actor.texture_sequence = ba.newnode(
            'texture_sequence', owner=actor.node, attrs={
                'rate': 30,
                'input_textures': (elon_mine_lit_tex,
                                   elon_mine_tex)})
        ba.timer(0.5, actor.texture_sequence.delete)
        ba.playsound(ba.getsound('activateBeep'),
                     position=actor.node.position)

        actor.aim = AutoAim(actor.node, actor.owner)
        # we now make it explodable.
        ba.timer(0.25, ba.WeakCall(actor._add_material,
                                   factory.land_mine_blast_material))
        actor.texture_sequence.connectattr('output_texture', actor.node,
                                           'color_texture')
