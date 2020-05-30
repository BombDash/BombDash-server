from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.gameutils import SharedObjects

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
        self.already_teleported = {}
        self.node_radius = radius / 1.75

        node_scale = {
            0: (0, 0, 0),
            0.5: (self.node_radius,
                  self.node_radius,
                  self.node_radius)
        }

        # portal materials
        self.first_portal_material = ba.Material()
        shared = SharedObjects.get()
        self.first_portal_material.add_actions(
            conditions=(('they_have_material',
                         shared.player_material)),
            actions=(('modify_part_collision', 'collide', True),
                     ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect',
                      self._first_portal_teleportation)))

        self.first_portal_material.add_actions(
            conditions=(('they_have_material',
                         shared.player_material),
                        'and', ('they_dont_have_material',
                                shared.player_material)),
            actions=(('modify_part_collision', 'collide', True),
                     ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._first_portal_handler)))

        self.second_portal_material = ba.Material()
        self.second_portal_material.add_actions(
            conditions=(('they_have_material',
                         shared.player_material)),
            actions=(('modify_part_collision', 'collide', True),
                     ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect',
                      self._second_portal_teleportation)))

        self.second_portal_material.add_actions(
            conditions=(('they_have_material',
                         shared.object_material),
                        'and', ('they_dont_have_material',
                                shared.player_material)),
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
        node = ba.getcollision().opposingnode
        name = node.get_name()

        if self.already_teleported.get(name):
            return

        def wrapper(nodename):
            self.already_teleported[nodename] = False

        hold_node = node.hold_node

        node.handlemessage(ba.StandMessage(
            position=self.second_node.position))

        if hold_node:
            self._first_portal_handler(hold_node, offset=(0, 1, 0))
            node.hold_node = hold_node

        self.already_teleported[name] = True
        ba.timer(1, ba.Call(wrapper, name))

    def _second_portal_teleportation(self):
        """Teleportation of a node that entered the second portal."""
        node = ba.getcollision().opposingnode
        name = node.get_name()

        if self.already_teleported.get(name):
            return

        def wrapper(nodename):
            self.already_teleported[nodename] = False

        hold_node = node.hold_node

        node.handlemessage(ba.StandMessage(
            position=self.first_node.position))

        if hold_node:
            self._second_portal_handler(hold_node, offset=(0, 1, 0))
            node.hold_node = hold_node

        self.already_teleported[name] = True
        ba.timer(1, ba.Call(wrapper, name))

    def _first_portal_handler(self, node=None, offset=(0, 0, 0)):
        """Checking a node before teleporting in the first portal."""
        if node is None:
            node = ba.getcollision().opposingnode
        name = node.get_name()

        if self.already_teleported.get(name):
            return
        velocity = node.velocity
        node.position = (
            self.second_position[0] + offset[0],
            self.second_position[1] + offset[1],
            self.second_position[2] + offset[2])

        def velocity_wrapper():
            if node:
                node.velocity = velocity

        ba.timer(0.001, velocity_wrapper)

        self.already_teleported[node.get_name()] = True

        def wrapper(nodename):
            self.already_teleported[nodename] = False

        ba.timer(1, ba.Call(wrapper, name))

    def _second_portal_handler(self, node=None, offset=(0, 0, 0)):
        """Checking a node before teleporting in the second portal."""
        if node is None:
            node = ba.getcollision().opposingnode

        name = node.get_name()

        if self.already_teleported.get(name):
            return

        velocity = node.velocity
        node.position = (
            self.first_position[0] + offset[0],
            self.first_position[1] + offset[1],
            self.first_position[2] + offset[2])

        def velocity_wrapper():
            if node:
                node.velocity = velocity

        ba.timer(0.01, velocity_wrapper)

        self.already_teleported[name] = True

        def wrapper(nodename):
            self.already_teleported[nodename] = False

        ba.timer(1, ba.Call(wrapper, name))
