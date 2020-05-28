from __future__ import annotations

from typing import TYPE_CHECKING

import random
import ba

from bastd.actor import playerspaz
from bd.locale import get_locale

if TYPE_CHECKING:
    from typing import Sequence, List, Any


class CompanionCube(ba.Actor):
    """He will heal you if you take it in your hands.

    Args:
        position (:obj:`tuple`, optional): Spawn position.
        velocity (:obj:`tuple`, optional): Speed and direction of travel.
    """

    def __init__(self, position: Sequence[float] = (0, 1, 0),
                 velocity: Sequence[float] = (0, 0, 0)):
        super().__init__()
        self.light: ba.Node
        self.picked: bool
        self.regen_timer = None
        self.phrase_text_node = None

        self.phrases: Sequence[Any] = get_locale('cube_companion_phrases')
        self.phrases_times: Sequence[float] = (
            10.0, 12.5, 15.0,
            17.5, 20.0, 22.5,
            25.0, 27.5, 30.0)

        self.phrases_time: float = random.choice(self.phrases_times)

        self.node: ba.Node = ba.newnode('prop', delegate=self, attrs={
            'body': 'crate',
            'model': ba.getmodel('tnt'),
            'light_model': ba.getmodel('tnt'),
            'color_texture': ba.gettexture('landMineLit'),
            'position': position,
            'velocity': velocity,
            'reflection': 'soft',
            'reflection_scale': [0.25],
            'materials': (ba.sharedobj('object_material'),
                          ba.sharedobj('footing_material'))})
        ba.animate(self.node, 'model_scale', {0: 0, 0.2: 1.3, 0.26: 1})

        self.spawn_random_phrase_timer: ba.Timer = ba.Timer(
            self.phrases_time,
            self._spawn_random_phrase,
            repeat=True)

    def _spawn_random_phrase(self) -> None:
        """Spawn a random phrase over a cube."""
        if self.node:
            self.phrases_time = random.choice(self.phrases_times)
            math: ba.Node = ba.newnode('math', owner=self.node, attrs={
                'input1': (0, 0.6, 0),
                'operation': 'add'})

            self.node.connectattr('position', math, 'input2')
            if self.phrase_text_node is not None:
                ba.animate(self.phrase_text_node, 'scale',
                           {0: 0.01, 0.5: 0})

                def wrapper():
                    self.phrase_text_node.delete()

                ba.timer(0.5, wrapper)

            def spawn_wrapper():
                if self.node.exists():
                    self.phrase_text_node = ba.newnode(
                        'text', owner=self.node, attrs={
                            'text': random.choice(self.phrases),
                            'scale': 0.0,
                            'in_world': True,
                            'h_align': 'center'})

                    math.connectattr(
                        'output', self.phrase_text_node, 'position')

                    ba.animate(self.phrase_text_node, 'scale', {
                        0: 0.0, 0.5: 0.01, 5: 0.01, 5.5: 0.0})

            ba.timer(1, spawn_wrapper)
        else:
            self.spawn_random_phrase_timer = None

    def handlemessage(self, msg):
        if isinstance(msg, ba.DieMessage):
            if self.node:
                self.node.delete()

        elif isinstance(msg, ba.OutOfBoundsMessage):  # Hmm, what? DieMessage calls too, don't it?
            if self.node:
                self.node.delete()

        elif isinstance(msg, ba.PickedUpMessage):
            self.node.extra_acceleration = (0, 25, 0)

            def up():
                if self.node.exists():
                    self.node.extra_acceleration = (0, 35, 0)

            ba.timer(0.3, up)

            def check():
                if not msg or not msg.node.exists():
                    self.node.extra_acceleration = (0, 0, 0)

            ba.timer(0.1, check)

            def regen():
                if (msg is not None and msg.node.exists()
                        and msg.node.getdelegate(playerspaz.PlayerSpaz).hitpoints
                        < msg.node.getdelegate(playerspaz.PlayerSpaz).hitpoints_max):
                    msg.node.getdelegate(playerspaz.PlayerSpaz).hitpoints += 1
                    msg.node.getdelegate(playerspaz.PlayerSpaz)._last_hit_time = None
                    msg.node.getdelegate(playerspaz.PlayerSpaz)._num_time_shit = 0
                    msg.node.hurt -= 0.001
                    ba.emitfx(
                        position=msg.node.position,
                        velocity=(0, 3, 0),
                        count=int(3.0 + random.random() * 5),
                        scale=1.5,
                        spread=0.3,
                        chunk_type='sweat')
                else:
                    self.regen_timer = None

            self.regen_timer = ba.Timer(0.01, regen, repeat=True)

        elif isinstance(msg, ba.DroppedMessage):
            self.regen_timer = None
            self.node.extra_acceleration = (0, 0, 0)

        elif isinstance(msg, ba.HitMessage):
            self.node.handlemessage('impulse',
                                    *msg.pos,
                                    *msg.velocity,
                                    msg.magnitude, msg.velocity_magnitude,
                                    msg.radius, 0,
                                    *msg.velocity)
