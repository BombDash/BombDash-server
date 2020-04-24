# Copyright (c) 2020 BombDash

from bastd.actor.spaz import Spaz as BaSpaz, stdbomb


def _decorator(f):
    def func(self: BaSpaz, *args, **kwargs):
        if self.sticky_gift_bomb_count > 0:
            self.set_sticky_gift_bomb_count(self.sticky_gift_bomb_count - 1)
            bomb_type = 'sticky_gift'
        elif self.portal_bomb_count > 0:
            self.set_portal_bomb_count(self.portal_bomb_count - 1)
            bomb_type = 'portal'
        elif self.health_bomb_count > 0:
            self.set_health_bomb_count(self.health_bomb_count - 1)
            bomb_type = 'health'
        elif self.airstrike_bomb_count > 0:
            self.set_airstrike_bomb_count(self.airstrike_bomb_count - 1)
            bomb_type = 'airstrike'
        elif self.elon_mine_count > 0:
            self.set_elon_mine_count(self.elon_mine_count - 1)
            bomb_type = 'elon_mine'
        elif self.holy_bomb_count > 0:
            self.set_holy_bomb_count(self.holy_bomb_count - 1)
            bomb_type = 'holy'
        else:
            return f(self, *args, **kwargs)
        pos = self.node.position_forward
        vel = self.node.velocity
        bomb = stdbomb.Bomb(position=(pos[0], pos[1] - 0.0, pos[2]),
                            velocity=(vel[0], vel[1], vel[2]),
                            bomb_type=bomb_type,
                            blast_radius=self.blast_radius,
                            source_player=self.source_player,
                            owner=self.node).autoretain()

        assert bomb.node
        self._pick_up(bomb.node)

        return bomb

    return func


BaSpaz.drop_bomb = _decorator(BaSpaz.drop_bomb)
