# Copyright (c) 2020 BombDash
from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.actor import spaz as stdspaz
from bd.me import powerup
from bd.actor import CompanionCube

if TYPE_CHECKING:
    pass


@powerup('speed', texture='powerupSpeed', freq=1)
def speed_callback(self: stdspaz.Spaz, msg: ba.PowerupMessage) -> None:
    # if ba.app.config.get('Powerup Popups', True):
    #     powerup_text = get_locale(
    #         'powerup_names')['speed']
    #
    #     PopupText(
    #         ba.Lstr(translate=('gameDescriptions', powerup_text)),
    #         color=(1, 1, 1),
    #         scale=1,
    #         position=self.node.position).autoretain()
    powerup_expiration_time = 10
    self.node.hockey = True

    def off_speed_wrapper():
        if self.node.exists():
            self.node.hockey = False

    ba.timer(powerup_expiration_time,
             off_speed_wrapper)

    tex = ba.gettexture('powerupSpeed')
    self._flash_billboard(tex)
    if self.powerups_expire:
        self.node.mini_billboard_2_texture = tex
        t = ba.time()
        self.node.mini_billboard_2_start_time = t
        self.node.mini_billboard_2_end_time = t + powerup_expiration_time


# FIXME: add cooldown or check what spaz is on ground
@powerup('high_jump', texture='buttonJump', freq=1)
def high_jump_callback(self: stdspaz.Spaz, msg: ba.PowerupMessage) -> None:
    # if ba.app.config.get('Powerup Popups', True):
    #     powerup_text = get_locale(
    #         'powerup_names')['jump_boost']
    #
    #     PopupText(
    #         ba.Lstr(translate=('gameDescriptions', powerup_text)),
    #         color=(1, 1, 1),
    #         scale=1,
    #         position=self.node.position).autoretain()

    powerup_expiration_time = 20

    def high_jump_wrapper():
        if not self.node.exists():
            return

        t = ba.time()
        if self.node.knockout <= 0 and self.node.frozen <= 0:
            self.node.jump_pressed = True
            ba.emitfx(
                position=(self.node.position[0],
                          self.node.position[1] - 0.5,
                          self.node.position[2]),
                velocity=(0, 0, 0),
                count=75,
                spread=0.5,
                chunk_type='spark')

            self.node.handlemessage(
                'impulse', self.node.position[0],
                self.node.position[1] + 10, self.node.position[2],
                0, 0, 0, 200, 200, 0, 0, 0, 200, 0)

        # self._turboFilterAddPress('jump')  # Это че?

    self.node.getdelegate().getplayer().assign_input_call(
        'jumpPress', high_jump_wrapper)

    def off_jump_boost_wrapper():
        if self.node.exists():
            self._jumpCooldown = 250
            # А это че?
            # self.node.getdelegate().getplayer().actor.connectControlsToPlayer()

    ba.timer(powerup_expiration_time,
             off_jump_boost_wrapper)

    tex = ba.gettexture('buttonJump')
    self._flash_billboard(tex)
    if self.powerups_expire:
        self.node.mini_billboard_2_texture = tex
        t = ba.time()
        self.node.mini_billboard_2_start_time = t
        self.node.mini_billboard_2_end_time = t + powerup_expiration_time


@powerup('heal_bombs', 'heart', freq=2, bomb_type='heal')
def health_bombs_callback(self: stdspaz.Spaz, msg: ba.PowerupMessage):
    self.inc_bomb_count('heal')


@powerup('companion_cube', 'landMineLit', freq=2)
def companion_cube_callback(self: stdspaz.Spaz, msg: ba.PowerupMessage):
    CompanionCube(
        position=(self.node.position[0],
                  self.node.position[1] + 1,
                  self.node.position[2]),
        velocity=(0, 10, 0)).autoretain()


@powerup('airstrike_bombs', 'menuIcon', freq=2, bomb_type='airstrike')
def airstrike_bombs_callback(self: stdspaz.Spaz, msg: ba.PowerupMessage):
    self.inc_bomb_count('airstrike')


@powerup('elon_mines', 'achievementMine', freq=123313, bomb_type='elon_mine')
def elon_mines_callback(self: stdspaz.Spaz, msg: ba.PowerupMessage):
    self.inc_bomb_count('elon_mine')
