from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.actor.playerspaz import PlayerSpaz
from bastd.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Optional, Sequence


class AutoAim:
    """Automatic item direction for player.

    Args:
        item (ba.Node): The node of the item.
        owner (ba.Node): The node of the player who used the item.
    """

    def __init__(self, item: ba.Node, owner: ba.Node):
        self.item = item
        self.owner = owner

        self.node: ba.Node
        self.target: Optional[ba.Node] = None

        self.aim_zone: ba.Material = ba.Material()
        shared = SharedObjects.get()
        self.aim_zone.add_actions(
            conditions=(('they_have_material',
                         shared.player_material)),
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

    def _touch_handler(self) -> None:
        """The action handler of an item if it touches a target."""
        node: ba.Node = ba.getcollision().opposingnode
        node_team: ba.Team = (node.getdelegate(PlayerSpaz).getplayer(ba.Player).team
                              if hasattr(node.getdelegate(PlayerSpaz), 'getplayer')
                              else None)

        owner_team = self.owner.getdelegate(PlayerSpaz).getplayer(ba.Player).team
        if (node.exists() and
                self.owner.exists() and
                self.item.exists() and
                node_team is not None and
                node_team != owner_team and
                node.getdelegate(PlayerSpaz).is_alive()):
            self.target = node
            self.node.delete()
            self.item.extra_acceleration = (0, 20, 0)
            self._move_item()

    def _move_item(self) -> None:
        """The movement of the item to the target."""
        if (self.target and
                self.target.exists() and
                self.item.exists()):
            item_velocity: Sequence[float] = self.item.velocity
            item_position: Sequence[float] = self.item.position
            target_position: Sequence[float] = self.target.position
            self.item.velocity = (
                item_velocity[0] + (target_position[0] - item_position[0]),
                item_velocity[1] + (target_position[1] - item_position[1]),
                item_velocity[2] + (target_position[2] - item_position[2]))

            ba.timer(0.001, self._move_item)

    def off(self) -> None:
        """Deleting a target."""
        self.target = None
