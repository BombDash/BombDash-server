# Copyright (c) 2020 BombDash

import random
import ba
import bastd.actor.bomb as stdbomb


class Airstrike(ba.Actor):
    """Bombing zone.

    Args:
        position (:obj:`tuple`, optional): Spawn position.
        velocity (:obj:`tuple`, optional): Speed and direction of travel.
        amount (:obj:`int`, optional): The number of bombs to be dropped.
        bomb_type (:obj:`str`, optional): Type of bombs to be dropped.
        highlight (:obj:`bool`, optional): To highlight the bombing zone.
    """

    def __init__(
            self, position=(0, 3, 0), velocity=(1, 1, 0),
            amount=5, bomb_type='impact', highlight=True):
        ba.Actor.__init__(self)
        self.position = position
        self.velocity = velocity
        self.amount = amount
        self.bomb_type = bomb_type

        self.drop_count = 0

        # highlight the bombing zone
        if highlight:
            self.area_highlight = ba.newnode('light', attrs={
                'color': (1, 0, 0),
                'position': position,
                'volume_intensity_scale': 1.0})

            # a little beautiful animation
            ba.animate(self.area_highlight, 'intensity',
                       {0: 0, 0.5: 1.0, 1: 0})

        # can be done without a timer?
        # or maybe the timer is the best option...
        self.drop_timer = ba.Timer(
            0.5, self._drop_bomb, repeat=True)

    def _drop_bomb(self):
        """Drop a certain amount of bombs."""
        if self.drop_count < self.amount:
            drop_position = (
                self.position[0] + random.uniform(1.5, -1.5),
                self.position[1] + 3,
                self.position[2] + random.uniform(1.5, -1.5)
            )

            stdbomb.Bomb(bomb_type=self.bomb_type,
                         position=drop_position,
                         velocity=self.velocity).autoretain()

            self.drop_count += 1
        else:
            self.drop_timer = None
