from __future__ import annotations

from typing import TYPE_CHECKING

import ba

from bd.me import redefine_class_methods, redefine_flag, RedefineFlag
from bastd.actor.spaz import Spaz
import random
import math

if TYPE_CHECKING:
    from typing import Sequence, Any, Optional


class Prefix(ba.Actor):
    """The prefix above the player head."""

    def __init__(
            self,
            owner: Optional[ba.Node] = None,
            prefix_text='Admin',
            prefix_speed=250,
            prefix_offset=(0, 1.75, 0),
            prefix_animation=(-65528, -16713473, -15335680),
            emit_type='spark',
            particle_type=1):
        super().__init__()
        self.owner = owner
        self.prefix_text = prefix_text
        self.prefix_speed = prefix_speed
        self.prefix_offset = prefix_offset
        self.prefix_animation = prefix_animation
        self.emit_type = emit_type
        self.particle_type = particle_type

        # for handle the effect of the third type
        self._offset = 0
        self._radius = 1

        emit_time = 60 if emit_type in ('sweat', 'spark') else 110
        if particle_type != 0:
            self.type_selection_handler_timer = ba.Timer(
                emit_time,
                self._type_selection_handler,
                repeat=True)

        self.math_node = ba.newnode('math', owner=self.owner, attrs={
            'input1': prefix_offset,
            'operation': 'add'})

        self.owner.connectattr('torso_position', self.math_node, 'input2')
        self.prefix_node = ba.newnode('text', owner=self.owner, attrs={
            'text': prefix_text,
            'scale': 0.01,
            'shadow': 0.5,
            'flatness': 0,
            'in_world': True,
            'h_align': 'center'})

        self.math_node.connectattr('output', self.prefix_node, 'position')
        # prefix color change animation
        prefix_animation = [
            [((i >> 16) & 255) / 255, ((i >> 8) & 255) / 255, (i & 255) / 255]
            for i in prefix_animation
        ]
        animation = {}
        count = 0
        for c in prefix_animation:
            animation[prefix_speed * count] = c
            count += 1
        animation[prefix_speed * count] = prefix_animation[0]
        # print(animation)

        ba.animate_array(self.prefix_node, 'color', 3, animation, True,
                         timeformat=ba.TimeFormat.MILLISECONDS)

    def _first_type_handler(self):
        owner_torso_pos = self.owner.torso_position
        position = (
            owner_torso_pos[0] - 0.25 + random.random() * 0.5,
            owner_torso_pos[1] - 0.25 + random.random() * 0.5,
            owner_torso_pos[2] - 0.25 + random.random() * 0.5)

        if self.emit_type in ('sweat', 'spark'):
            spread = 0.1
            scale = random.random() * 0.8
            owner_vel = self.owner.velocity
            vel = 4 if not self.emit_type == 'ice' else 0
            velocity = (
                (-vel + (random.random() * (vel * 2))) + owner_vel[0] * 2,
                (-vel + (random.random() * (vel * 2))) + owner_vel[1] * 4,
                (-vel + (random.random() * (vel * 2))) + owner_vel[2] * 2
            )
        else:
            spread = 0.15
            velocity = (0, 0, 0)
            scale = random.random() * 0.6

        ba.emitfx(position=position,
                  velocity=velocity,
                  count=10,
                  scale=scale,
                  spread=spread,
                  chunk_type=self.emit_type)

    def _second_type_handler(self):
        position = (
            self.owner.position[0],
            self.owner.position[1] - 0.25,
            self.owner.position[2]
        )

        ba.emitfx(position=position,
                  count=10,
                  scale=0.1 + random.random(),
                  spread=0.15,
                  chunk_type=self.emit_type)

    def _third_type_handler(self):
        sin = math.sin(self._offset) * self._radius
        cos = math.cos(self._offset) * self._radius
        self._offset += 0.1
        position = (
            self.owner.position[0] + cos,
            self.owner.position[1],
            self.owner.position[2] + sin
        )

        ba.emitfx(position=position,
                  count=5,
                  scale=1,
                  spread=0,
                  chunk_type=self.emit_type)

    def _fourth_type_handler(self):
        position = (
            self.owner.position[0],
            self.owner.position[1] - 0.5,
            self.owner.position[2]
        )

        ba.emitfx(position=position,
                  count=10,
                  scale=0.1 + random.random(),
                  spread=0.001,
                  chunk_type=self.emit_type,
                  emit_type='stickers')

    def _type_selection_handler(self):
        if self.owner and not self.owner.dead:
            if self.particle_type == 1:
                self._first_type_handler()
            elif self.particle_type == 2:
                self._second_type_handler()
            elif self.particle_type == 3:
                self._third_type_handler()
            elif self.particle_type == 4:
                self._fourth_type_handler()

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.DieMessage):
            self.math_node.delete()
            self.prefix_node.delete()


@redefine_class_methods(Spaz)
class Spaz(ba.Actor):
    _redefine_methods = '__init__'.split()

    @redefine_flag(RedefineFlag.DECORATE_AFTER)
    def __init__(self,
                 color: Sequence[float] = (1.0, 1.0, 1.0),
                 highlight: Sequence[float] = (0.5, 0.5, 0.5),
                 character: str = 'Spaz',
                 source_player: ba.Player = None,
                 start_invincible: bool = True,
                 can_accept_powerups: bool = True,
                 powerups_expire: bool = False,
                 demo_mode: bool = False,
                 returned: Any = None):
        self.prefix = Prefix(self.node)
