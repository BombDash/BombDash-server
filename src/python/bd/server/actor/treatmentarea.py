# Copyright (c) 2020 BombDash


import ba


class TreatmentArea(ba.Actor):
    """The area in which players receive health kit.

    Args:
        position (:obj:`tuple`, optional): Spawn position.
        lifetime (:obj:`int`, optional): Treatment area and highlight life.
        highlight (:obj:`bool`, optional): To highlight the treatment area.
    """

    def __init__(self, position=(0, 1, 0), lifetime=0.5, highlight=True):
        super().__init__()
        # array of nodes that received health kit
        self.cured_nodes = []

        self.area_material = ba.Material()
        self.area_material.add_actions(
            conditions=(('they_have_material',
                         ba.sharedobj('player_material'))),
            actions=(('modify_part_collision', 'collide', True),
                     ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._touch_handler)))

        # the area itself...
        self.node = ba.newnode('region', attrs={
            'type': 'sphere',
            'scale': (2, 2, 2),
            'position': position,
            'materials': [self.area_material]})

        ba.timer(lifetime, self.node.delete)

        # highlight the treatment area
        if highlight:
            self.area_highlight = ba.newnode('light', attrs={
                'color': (1, 1, 1),
                'radius': 0.25,
                'position': position,
                'volume_intensity_scale': 1.0})

            # a little beautiful animation
            ba.animate(self.area_highlight, 'intensity',
                       {0: 0, lifetime / 2: 1.0, lifetime: 0})

    def _touch_handler(self):
        """The action handler of an item if it touches a target."""
        node = ba.get_collision_info('opposing_node')
        if node not in self.cured_nodes:
            node.handlemessage(ba.PowerupMessage(
                poweruptype='health'))

            self.cured_nodes.append(node)
