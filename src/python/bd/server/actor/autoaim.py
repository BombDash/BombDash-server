# Copyright (c) 2020 BombDash

import ba


class AutoAim:
    """Automatic item direction for player.

    Args:
        item (bs.Node): The node of the item.
        owner (bs.Node): The node of the player who used the item.
    """

    def __init__(self, item, owner):
        self.item = item
        self.owner = owner

        self.node = None
        self.target = None

        self.aim_zone = ba.Material()
        self.aim_zone.add_actions(
            conditions=(('they_have_material',
                         ba.sharedobj('player_material'))),
            actions=(('modify_part_collision', 'collide', True),
                     ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._touch_handler)))

        # raise the item a little
        self.item.extra_acceleration = (0, 20, 0)
        # if the item exists, then take its position,
        # else "turn the bench"
        if self.item.exists():
            position = self.item.position
        else:
            return

        self.node = ba.newnode('region', attrs={
            'type': 'sphere',
            'position': position,
            'materials': [self.aim_zone]})

        # aiming effect
        ba.animate_array(self.node, 'scale', 3,
                         {0: (0.1, 0.1, 0.1), 1: (60, 60, 60)})

    def _touch_handler(self):
        """The action handler of an item if it touches a target."""
        node = ba.get_collision_info('opposing_node')
        node_team = (node.getdelegate().getplayer().team
                     if hasattr(node.getdelegate(), 'getplayer')
                     else None)

        owner_team = self.owner.getdelegate().getplayer().team
        if (node.exists() and
                self.owner.exists() and
                self.item.exists() and
                node_team is not None and
                node_team != owner_team and
                node.getdelegate().is_alive()):
            self.target = node
            self.node.delete()
            self.item.extra_acceleration = (0, 20, 0)
            self._move_item()

    def _move_item(self):
        """The movement of the item to the target."""
        if (self.target and
                self.target.exists() and
                self.item.exists()):
            item_velocity = self.item.velocity
            item_position = self.item.position
            target_position = self.target.position
            self.item.velocity = (
                item_velocity[0] + (target_position[0] - item_position[0]),
                item_velocity[1] + (target_position[1] - item_position[1]),
                item_velocity[2] + (target_position[2] - item_position[2]))

            ba.timer(0.001, self._move_item)

    def off(self):
        """Deleting a target."""
        self.target = None
