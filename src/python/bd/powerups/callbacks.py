# Copyright (c) 2020 BombDash
from __future__ import annotations

from typing import TYPE_CHECKING

import random

import ba
from bastd.actor import spaz as stdspaz
from bastd.actor import powerupbox as stdpowerup
from bastd.actor import bomb as stdbomb
from bastd.actor import spazbot as stdbot
from bastd.actor import playerspaz
from bd.me import powerup
from bd.actor import CompanionCube

if TYPE_CHECKING:
    pass


@powerup('speed', texture='powerupSpeed', freq=1)
def speed_callback(self: stdspaz.Spaz, msg: ba.PowerupMessage) -> None:
    powerup_expiration_time = 10
    tex = ba.gettexture('powerupSpeed')

    self._flash_billboard(tex)
    if self.powerups_expire:
        self.node.mini_billboard_1_texture = tex
        t = ba.time()
        self.node.mini_billboard_1_start_time = t
        self.node.mini_billboard_1_end_time = t + powerup_expiration_time

    if self.node.hockey:
        return

    self.node.hockey = True

    def off_speed_wrapper():
        if self.node.exists():
            self.node.hockey = False

    ba.timer(powerup_expiration_time,
             off_speed_wrapper)


@powerup('jetpack', texture='buttonJump', freq=1)
def jetpack_callback(self: stdspaz.Spaz, msg: ba.PowerupMessage) -> None:
    powerup_expiration_time = 5

    tex = ba.gettexture('buttonJump')

    self._flash_billboard(tex)
    if self.powerups_expire:
        self.node.mini_billboard_1_texture = tex
        t = ba.time()
        self.node.mini_billboard_1_start_time = t
        self.node.mini_billboard_1_end_time = t + powerup_expiration_time

    def _jetpack_wrapper():
        if not self.node.exists():
            return

        if self.node.knockout <= 0 and self.node.frozen <= 0:
            self.node.jump_pressed = True
            ba.emitfx(
                position=(self.node.position[0],
                          self.node.position[1] - 0.5,
                          self.node.position[2]),
                velocity=(0, -10, 0),
                count=75,
                spread=0.25,
                chunk_type='spark')

    def jetpack_wrapper():
        self.node.handlemessage(
            'impulse', self.node.position[0],
            self.node.position[1] + 10, self.node.position[2],
            0, 0, 0, 150, 20, 0, 0, 0, 150, 0)

        for i in range(0, 200, 50):
            ba.timer(i, _jetpack_wrapper, timeformat=ba.TimeFormat.MILLISECONDS)

        # self._turboFilterAddPress('jump')  # Это че?

    self.node.getdelegate(playerspaz.PlayerSpaz).getplayer(ba.Player).assign_input_call(
        'jumpPress', jetpack_wrapper)

    def off_jetpack_wrapper():
        if self.node.exists():
            # self._jumpCooldown = 250
            self.node.getdelegate(playerspaz.PlayerSpaz).connect_controls_to_player()

    ba.timer(powerup_expiration_time,
             off_jetpack_wrapper)

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
        velocity=(0, 5, 0)).autoretain()


@powerup('airstrike_bombs', 'menuIcon', freq=2, bomb_type='airstrike')
def airstrike_bombs_callback(self: stdspaz.Spaz, msg: ba.PowerupMessage):
    self.inc_bomb_count('airstrike')


@powerup('elon_mines', 'achievementMine', freq=1, bomb_type='elon_mine')
def elon_mines_callback(self: stdspaz.Spaz, msg: ba.PowerupMessage):
    self.inc_bomb_count('elon_mine')


@powerup('portal_bombs', 'light', freq=1, bomb_type='portal_bomb')
def portal_bombs_callback(self: stdspaz.Spaz, msg: ba.PowerupMessage):
    self.inc_bomb_count('portal_bomb')


@powerup('sticky_gift_bombs', 'achievementCrossHair', freq=1, bomb_type='sticky_gift')
def portal_bombs_callback(self: stdspaz.Spaz, msg: ba.PowerupMessage):
    self.inc_bomb_count('sticky_gift')


@powerup('lucky_block', 'achievementEmpty', freq=2)
def lucky_block_callback(self: stdspaz.Spaz, msg: ba.PowerupMessage):
    event_number = random.randint(1, 15)

    if event_number in (1, 2, 3):
        powerup_type = stdpowerup.PowerupBoxFactory(
        ).get_random_powerup_type()

        self.node.handlemessage(
            ba.PowerupMessage(poweruptype=powerup_type))
    elif event_number == 4:
        ba.camerashake(1)
        ba.emitfx(
            position=(self.node.position[0],
                      self.node.position[1] + 4,
                      self.node.position[2]),
            velocity=(0, 0, 0),
            count=700,
            spread=0.7,
            chunk_type='spark')

        powerup_type = stdpowerup.PowerupBoxFactory.get().get_random_powerup_type()

        stdpowerup.PowerupBox(
            position=(self.node.position[0],
                      self.node.position[1] + 4,
                      self.node.position[2]),
            poweruptype=powerup_type,
            expire=True).autoretain()

        powerup_type = stdpowerup.PowerupBoxFactory.get(
        ).get_random_powerup_type()

        stdpowerup.PowerupBox(
            position=(self.node.position[0],
                      self.node.position[1] + 4,
                      self.node.position[2]),
            poweruptype=powerup_type,
            expire=True).autoretain()

        powerup_type = stdpowerup.PowerupBoxFactory.get().get_random_powerup_type()

        stdpowerup.PowerupBox(
            position=(self.node.position[0],
                      self.node.position[1] + 4,
                      self.node.position[2]),
            poweruptype=powerup_type,
            expire=True).autoretain()
    elif event_number == 5:
        stdbomb.Bomb(
            position=(self.node.position[0],
                      self.node.position[1] + 3,
                      self.node.position[2]),
            source_player=self.source_player,
            owner=self.node,
            blast_radius=6).autoretain()
    elif event_number == 6:
        self.node.handlemessage(ba.FreezeMessage())
    elif event_number == 7:
        chunk_type = (
            'ice',
            'rock',
            'metal',
            'spark',
            'splinter',
            'slime')

        ba.emitfx(
            position=self.node.position,
            velocity=(random.random() * 2,
                      random.random() * 2,
                      random.random() * 2),
            count=600,
            spread=random.random(),
            chunk_type=random.choice(chunk_type))

        ba.camerashake(1)
        ba.playsound(ba.getsound('corkPop'))  # position=self.node.position?
    elif event_number == 8:
        position = self.node.position

        def rain_wrapper():
            p_type = stdpowerup.PowerupBoxFactory.get().get_random_powerup_type()

            new_position = (
                -10 + position[0] + random.random() * 20,
                position[1] + 6,
                -10 + position[2] + random.random() * 20
            )

            stdpowerup.PowerupBox(poweruptype=p_type,
                                  position=new_position).autoretain()

            if random.random() > 0.04:
                ba.timer(0.1, rain_wrapper)

        rain_wrapper()
    elif event_number == 9:
        stdbomb.Blast(position=self.node.position,
                      velocity=self.node.velocity,
                      blast_radius=1.0,
                      blast_type='normal',
                      source_player=None,
                      hit_type='punch',
                      hit_subtype='normal')
    elif event_number == 10:  # Blast-square under spaz
        x = self.node.position[0] - 2
        while x < self.node.position[0] + 2:
            y = self.node.position[2] - 2
            while y < self.node.position[2] + 2:
                stdbomb.Blast(
                    position=(x, self.node.position[1], y),
                    velocity=(self.node.velocity[0],
                              self.node.velocity[1] + 10,
                              self.node.velocity[2]),
                    blast_radius=0.5,
                    blast_type='normal',
                    source_player=None,
                    hit_type='punch',
                    hit_subtype='normal')

                y += 1

            x += 1
    elif event_number == 11:
        offset = -15
        case = 1 if random.random() < 0.5 else -1
        while offset < 15:
            velocity = (case * (12 + 8 * random.random()), -0.1, 0)
            stdbomb.Bomb(bomb_type='tnt',
                         position=(self.node.position[0] - case * 10,
                                   self.node.position[1] + 3,
                                   self.node.position[2] + offset),
                         velocity=velocity).autoretain()

            offset += 1.5
    elif event_number == 12:
        color = {
            0.0: (0, 0, 3),
            0.5: (0, 3, 0),
            1.0: (3, 0, 0),
            1.5: (0, 0, 3)
        }

        # FIXME
        # ba.animate_array(self.node, 'color', 3, color, True)
        # self.node.handlemessage('celebrate', 100000000)
    elif event_number == 13:
        CompanionCube(
            position=(self.node.position[0],
                      self.node.position[1] + 1,
                      self.node.position[2]),
            velocity=(0, 10, 0)).autoretain()
    elif event_number == 14:
        ba.emitfx(position=self.node.position,
                  count=100,
                  emit_type='tendrils',
                  tendril_type='smoke')

    elif event_number == 15:
        def drop_man():
            botset: stdbot.SpazBotSet
            activity = ba.getactivity()
            if not hasattr(activity, 'botset'):
                activity.botset = botset = stdbot.SpazBotSet()
            botset = activity.botset
            aoi_bounds = self.activity.globalsnode.area_of_interest_bounds
            botset.spawn_bot(stdbot.BrawlerBotLite,
                             (random.randrange(int(aoi_bounds[0]), int(aoi_bounds[3]) + 1),
                              aoi_bounds[4] - 1,
                              random.randrange(int(aoi_bounds[2]), int(aoi_bounds[5]) + 1)),
                             spawn_time=0.001)

        def lightning_bolt(position, radius=1):
            ba.camerashake(4)
            vignette_outer = self.activity.globalsnode.vignette_outer
            # if ba.getactivity().tint is None:
            #     ba.getactivity().std_tint = ba.sharedobj('globals').vignette_outer
            #     vignette_outer = ba.sharedobj('globals').vignette_outer
            # else:
            #     vignette_outer = ba.getactivity().tint

            light = ba.newnode('light', attrs={
                'position': position,
                'color': (0.4, 0.4, 0.8),
                'volume_intensity_scale': 1.0,
                'radius': radius})

            ba.animate(light, 'intensity', {
                0: 1,
                50: radius,
                150: radius / 2,
                250: 0,
                260: radius,
                410: radius / 2,
                510: 0}, 
                timeformat=ba.TimeFormat.MILLISECONDS,
                suppress_format_warning=True)

            ba.animate_array(self.activity.globalsnode, 'vignette_outer', 3, {
                0: vignette_outer, 0.2: (0.2, 0.2, 0.2), 0.51: vignette_outer})

            # ba.playsound(
            #     ba.getsound('grom'),
            #     volume=10,
            #     position=(0, 10, 0))

        lightning_bolt(self.node.position)

        for time in range(15):
            ba.timer(time, drop_man)
