from __future__ import annotations

from typing import TYPE_CHECKING

import ba

if TYPE_CHECKING:
    from typing import Sequence, List


class TreatmentArea(ba.Actor):
    """The area in which players receive health kit.

    Args:
        position (:obj:`tuple`, optional): Spawn position.
        lifetime (:obj:`int`, optional): Treatment area and highlight life.
        highlight (:obj:`bool`, optional): To highlight the treatment area.
    """

    def __init__(self, position: Sequence[float] = (0, 1, 0), lifetime: float = 0.5,
                 highlight: bool = True):
        super().__init__()
        # array of nodes that received health kit
        self.cured_nodes: List[ba.Node] = []

        self.area_material: ba.Material = ba.Material()
        self.area_material.add_actions(
            conditions=(('they_have_material',
                         ba.sharedobj('player_material'))),
            actions=(('modify_part_collision', 'collide', True),
                     ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._touch_handler)))

        # the area itself...
        self.node: ba.Node = ba.newnode('region', attrs={
            'type': 'sphere',
            'scale': (2, 2, 2),
            'position': position,
            'materials': [self.area_material]})

        ba.timer(lifetime, self.node.delete)

        # highlight the treatment area
        if highlight:
            self.area_highlight: ba.Node = ba.newnode('light', attrs={
                'color': (1, 1, 1),
                'radius': 0.25,
                'position': position,
                'volume_intensity_scale': 1.0})

            # a little beautiful animation
            ba.animate(self.area_highlight, 'intensity',
                       {0: 0, lifetime / 2: 1.0, lifetime: 0})

    def _touch_handler(self):
        """The action handler of an item if it touches a target."""
        node: ba.Node = ba.getcollision().opposingnode
        if node not in self.cured_nodes:
            node.handlemessage(ba.PowerupMessage(
                poweruptype='health'))

            self.cured_nodes.append(node)
