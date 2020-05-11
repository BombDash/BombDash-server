from __future__ import annotations

from typing import TYPE_CHECKING

import random
import ba
import bastd.actor.bomb as stdbomb

if TYPE_CHECKING:
    from typing import Sequence, List, Any


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
            self, position: Sequence[float] = (0, 3, 0), velocity: Sequence[float] = (0, -5, 0),
            amount: int = 15, bomb_type: str = 'impact', highlight: bool = True):
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

            ba.animate(self.area_highlight, 'intensity',
                       {0: 0, 0.5: 1.0, 1: 0})

        def wrapper():
            self.drop_timer = ba.Timer(
                0.25, self._drop_bomb, repeat=True)

        ba.timer(1, wrapper)

    def _drop_bomb(self):
        """Drop a certain amount of bombs."""
        if self.drop_count < self.amount:
            highest_pos = self.position[1] + 3
            activity = ba.getactivity()
            if isinstance(activity, ba.GameActivity):
                highest_pos = activity.map.get_def_bound_box('area_of_interest_bounds')[4]
            drop_position = (
                self.position[0] + random.uniform(1.5, -1.5),
                highest_pos,
                self.position[2] + random.uniform(1.5, -1.5))

            stdbomb.Bomb(bomb_type=self.bomb_type,
                         position=drop_position,
                         blast_radius=1,
                         velocity=self.velocity).autoretain()

            self.drop_count += 1
        else:
            self.drop_timer = None
