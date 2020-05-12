from __future__ import annotations

from typing import TYPE_CHECKING

import ba

if TYPE_CHECKING:
    from typing import Sequence, List, Any


class Portals(ba.Actor):
    """Two portals.

    Args:
        color (:obj:`tuple`, optional): Portals colors.
        radius (:obj:`float`, optional): Portals volume radius.
        first_position (:obj:`tuple`, optional): First portal position.
        second_position (:obj:`tuple`, optional): Second portal position.
    """

    def __init__(
            self,
            color=(1, 1, 1),
            radius=1.25,
            first_position=(-3, 1, 0),
            second_position=(3, 1, 0)):
        super().__init__()
        self.first_position = first_position
        self.second_position = second_position
        self.radius = radius

        # self.cooldown = False
        self.already_teleported = False
        self.node_radius = radius / 1.75

        node_scale = {
            0: (0, 0, 0),
            0.5: (self.node_radius,
                  self.node_radius,
                  self.node_radius)
        }

        # portal materials
        self.first_portal_material = ba.Material()
        self.first_portal_material.add_actions(
            conditions=(('they_have_material',
                         ba.sharedobj('player_material'))),
            actions=(('modify_part_collision', 'collide', True),
                     ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect',
                      self._first_portal_teleportation)))

        self.first_portal_material.add_actions(
            conditions=(('they_have_material',
                         ba.sharedobj('object_material')),
                        'and', ('they_dont_have_material',
                                ba.sharedobj('player_material'))),
            actions=(('modify_part_collision', 'collide', True),
                     ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._first_portal_handler)))

        self.second_portal_material = ba.Material()
        self.second_portal_material.add_actions(
            conditions=(('they_have_material',
                         ba.sharedobj('player_material'))),
            actions=(('modify_part_collision', 'collide', True),
                     ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect',
                      self._second_portal_teleportation)))

        self.second_portal_material.add_actions(
            conditions=(('they_have_material',
                         ba.sharedobj('object_material')),
                        'and', ('they_dont_have_material',
                                ba.sharedobj('player_material'))),
            actions=(('modify_part_collision', 'collide', True),
                     ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._second_portal_handler)))

        # create a first portal
        self.first_node = ba.newnode('region', attrs={
            'type': 'sphere',
            'position': self.first_position,
            'materials': [self.first_portal_material]})

        self.first_node_visualization = ba.newnode('shield', attrs={
            'color': color,
            'position': self.first_position})

        ba.animate(self.first_node_visualization, 'radius',
                   {0: 0, 0.5: radius})

        # ba.animate_array(self.first_node, 'scale', 3, node_scale)

        # create a second portal
        self.second_node = ba.newnode('region', attrs={
            'type': 'sphere',
            'position': self.second_position,
            'materials': [self.second_portal_material]})

        self.second_node_visualization = ba.newnode('shield', attrs={
            'color': color,
            'position': self.second_position})

        ba.animate(self.second_node_visualization, 'radius',
                   {0: 0, 0.5: radius})

        # ba.animate_array(self.second_node, 'scale', 3, node_scale)

        # delete portals after some time
        ba.timer(10, self.delete)

    def delete(self):
        """Delete all portals and their visualization."""
        self.first_node.delete()
        self.second_node.delete()
        self.first_node_visualization.delete()
        self.second_node_visualization.delete()

    def _first_portal_teleportation(self):
        """Teleportation of a node that entered the first portal."""
        if self.already_teleported:
            return

        node = ba.get_collision_info('opposing_node')

        def wrapper():
            self.already_teleported = False

        node.handlemessage(ba.StandMessage(
            position=self.second_node.position))

        self.already_teleported = True
        ba.timer(1, wrapper)

    def _second_portal_teleportation(self):
        """Teleportation of a node that entered the second portal."""
        if self.already_teleported:
            return

        node = ba.get_collision_info('opposing_node')

        def wrapper():
            self.already_teleported = False

        node.handlemessage(ba.StandMessage(
            position=self.first_node.position))

        self.already_teleported = True
        ba.timer(1, wrapper)

    def _first_portal_handler(self):
        """Checking a node before teleporting in the first portal."""
        if self.already_teleported:
            return

        node = ba.get_collision_info('opposing_node')

        velocity = node.velocity
        node.position = self.second_position

        def velocity_wrapper():
            if node:
                node.velocity = velocity

        ba.timer(0.01, velocity_wrapper)

        self.already_teleported = True

        def wrapper():
            self.already_teleported = False

        ba.timer(1, wrapper)

    def _second_portal_handler(self):
        """Checking a node before teleporting in the second portal."""
        if self.already_teleported:
            return

        node = ba.get_collision_info('opposing_node')

        velocity = node.velocity
        node.position = self.first_position

        def velocity_wrapper():
            if node:
                node.velocity = velocity

        ba.timer(0.01, velocity_wrapper)

        self.already_teleported = True

        def wrapper():
            self.already_teleported = False

        ba.timer(1, wrapper)

