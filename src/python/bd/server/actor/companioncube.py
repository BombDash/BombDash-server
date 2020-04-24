# Copyright (c) 2020 BombDash

import random
import ba


def get_locale(*args, **kwargs):  # TODO: create get_locate function
    if args[0] == 'cube_companion_phrases':
        return 'Не бей пж', 'Я жив!', 'Ураа!'


class CompanionCube(ba.Actor):
    """He will heal you if you take it in your hands.

    Args:
        position (:obj:`tuple`, optional): Spawn position.
        velocity (:obj:`tuple`, optional): Speed and direction of travel.
    """

    def __init__(self, position=(0, 1, 0), velocity=(0, 0, 0)):
        super().__init__()
        self.light = None
        self.picked = None
        self.regen_timer = None
        self.phrase_text_node = None

        self.phrases = get_locale('cube_companion_phrases')
        self.phrases_times = (
            10.0, 12.5, 15.0,
            17.5, 20.0, 22.5,
            25.0, 27.5, 30.0)

        self.phrases_time = random.choice(self.phrases_times)

        self.node = ba.newnode('prop', delegate=self, attrs={
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

        self.spawn_random_phrase_timer = ba.Timer(
            self.phrases_time,
            self._spawn_random_phrase,
            repeat=True)

    def _spawn_random_phrase(self):
        """Spawn a random phrase over a cube."""
        if self.node.exists():
            self.phrases_time = random.choice(self.phrases_times)
            math = ba.newnode('math', owner=self.node, attrs={
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
            if self.node.exists():
                self.node.delete()

        elif isinstance(msg, ba.OutOfBoundsMessage):
            if self.node.exists():
                self.node.delete()

        elif isinstance(msg, ba.PickedUpMessage):
            self.picked = True
            self.node.extraAcceleration = (0, 25, 0)

            def up():
                if self.node.exists():
                    self.node.extraAcceleration = (0, 35, 0)

            ba.timer(0.3, up)

            def check():
                if not msg or not msg.node.exists():
                    self.node.extraAcceleration = (0, 0, 0)

            ba.timer(0.1, check)

            def regen():
                if (msg is not None and msg.node.exists()
                        and msg.node.getdelegate().hitpoints
                        < msg.node.getdelegate().hitpoints_max):
                    msg.node.getdelegate().hitpoints += 1
                    msg.node.getdelegate()._last_hit_time = None
                    msg.node.getdelegate()._num_time_shit = 0
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
            self.picked = False
            self.regen_timer = None
            self.node.extraAcceleration = (0, 0, 0)

        elif isinstance(msg, ba.HitMessage):
            self.node.handlemessage(
                'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                msg.velocity[0], msg.velocity[1], msg.velocity[2],
                msg.magnitude, msg.velocity_magnitude, msg.radius,
                0, msg.velocity[0], msg.velocity[1], msg.velocity[2])
