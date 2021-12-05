# Copyright (c) 2020 BombDash
from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

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
    powerup_expiration_time = 10_000
    tex = ba.gettexture('powerupSpeed')

    # noinspection DuplicatedCode
    self._flash_billboard(tex)
    if self.powerups_expire:
        self.node.mini_billboard_1_texture = tex
        t = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
        self.node.mini_billboard_1_start_time = t
        self.node.mini_billboard_1_end_time = t + powerup_expiration_time

        def _speed_wear_off_flash() -> None:
            if self.node:
                self.node.billboard_texture = tex
                self.node.billboard_opacity = 1.0
                self.node.billboard_cross_out = True

        def _speed_wear_off() -> None:
            if self.node:
                ba.playsound(stdpowerup.PowerupBoxFactory.get().powerdown_sound,
                             position=self.node.position)
                self.node.billboard_opacity = 0.0
                self.node.hockey = False

        self._jetpack_wear_off_flash_timer = (ba.Timer(
            powerup_expiration_time - 2000,
            _speed_wear_off_flash,
            timeformat=ba.TimeFormat.MILLISECONDS))
        self._jetpack_wear_off_timer = (ba.Timer(
            powerup_expiration_time,
            _speed_wear_off,
            timeformat=ba.TimeFormat.MILLISECONDS))

    if self.node.hockey:
        return

    self.node.hockey = True


@powerup('jetpack', texture='buttonJump', freq=1)
def jetpack_callback(self: stdspaz.Spaz, msg: ba.PowerupMessage) -> None:
    powerup_expiration_time = 10_000

    tex = ba.gettexture('buttonJump')

    self._flash_billboard(tex)
    if self.powerups_expire:
        self.node.mini_billboard_2_texture = tex
        t = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
        self.node.mini_billboard_2_start_time = t
        self.node.mini_billboard_2_end_time = t + powerup_expiration_time

        def _jetpack_wear_off_flash() -> None:
            if self.node:
                self.node.billboard_texture = tex
                self.node.billboard_opacity = 1.0
                self.node.billboard_cross_out = True

        def _jetpack_wear_off() -> None:
            if self.node:
                ba.playsound(stdpowerup.PowerupBoxFactory.get().powerdown_sound,
                             position=self.node.position)
                self.node.billboard_opacity = 0.0
                self.node.getdelegate(playerspaz.PlayerSpaz).connect_controls_to_player()

        self._jetpack_wear_off_flash_timer = (ba.Timer(
            powerup_expiration_time - 2000,
            _jetpack_wear_off_flash,
            timeformat=ba.TimeFormat.MILLISECONDS))
        self._jetpack_wear_off_timer = (ba.Timer(
            powerup_expiration_time,
            _jetpack_wear_off,
            timeformat=ba.TimeFormat.MILLISECONDS))

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

    self.node.getdelegate(playerspaz.PlayerSpaz).getplayer(ba.Player).assigninput(
        ba.InputType.JUMP_PRESS, jetpack_wrapper)


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
    elif event_number == 10:
        def blast(x: int, y: int, z: int) -> None:
            # add sound
            ba.NodeActor(node=ba.newnode('scorch',
                                         attrs={
                                             'position': (x, z, y),
                                             'size': 0.2,
                                             'big': False,
                                         })).autoretain()

        def smoke(x: int, y: int, z: int) -> None:
            ba.emitfx(position=(x, z, y),
                      velocity=(0, 2, 0),
                      count=1,
                      emit_type='tendrils',
                      tendril_type='smoke')
            ba.emitfx(position=(x, z, y),
                      velocity=(0, 2, 0),
                      count=int(1.0 + random.random() * 2),
                      scale=0.8,
                      spread=1.5,
                      chunk_type='spark')

        star_positions = [
            (2, 0),
            (0, 2),
            (-1.2, -1.6),
            (1.82, 0.83),
            (-1.83, 0.82),
            (1.23, -1.57),
            (-1.25, 1.56),
            (-0.65, 1.89),
            (0.82, 1.82),
            (1.27, 1.55),
            (1.82, -0.84),
            (0.31, -1.98),
            (-0.42, -1.96),
            (-1.75, -0.96),
            (-2, -0.14),
            (-0.69, -0.07),
            (-0.39, 0.82),
            (0.41, 0.82),
            (0.71, -0.06),
            (0.01, -0.62),
            (-0.99, 0.82),
            (-1.26, 0.37),
            (-0.89, -0.65),
            (-0.52, -1.05),
            (0.59, -1.07),
            (0.96, -0.8),
            (1.22, 0.35),
            (1.07, 0.82),
            (0.21, 1.39),
            (-0.17, 1.48),
            # ---
            (-1.94, 0.47),
            (-1.51, 1.31),
            (-0.95, 1.76),
            (-0.38, 1.96),
            (0.45, 1.95),
            (1.05, 1.7),
            (1.57, 1.24),
            (1.94, 0.49),
            (1.96, -0.42),
            (1.62, -1.17),
            (0.84, -1.82),
            (-0.78, -1.84),
            (-1.5, -1.33),
            (-1.91, -0.59),
            (-1.99, 0.17),
            (-1, 0.17),
            (-0.7, 0.82),
            (-0.27, 1.19),
            (0.29, 1.15),
            (0.77, 0.82),
            (1, 0.17),
            (0.84, -0.42),
            (0.31, -0.85),
            (-0.8, -1.27),
            (-1, -1),
            (-0.56, 0.33),
            (-0.47, 0.61),
            (0.52, 0.51),
            (-0.1, 0.82),
            (0.13, 0.82),
            (0.6, 0.27),
            (0.46, -0.27),
            (0.29, -0.4),
            (-0.44, -0.27),
            (-0.24, -0.42),
            (-1.36, 0.82),
            (-1.53, 0.59),
            (1.35, 0.83),
            (1.55, 0.61),
            (0.85, -1.28),
            (1.08, -1.13),
            (0.78, -0.34),
            (-0.21, -0.8),
            (0.11, 1.68)
        ]

        class Sparkling(ba.Actor):
            def __init__(self, position: Sequence[float], target: ba.Node):
                super().__init__()
                # nah; nodes not needed
                self.position = position
                self.position = (self.position[0], self.position[1] + 0.5, self.position[2])
                self.target = target

                ba.timer(0.001, ba.WeakCall(self._update))

            def _sparkle(self):
                ba.emitfx(position=self.position,
                          velocity=(0, 1, 0),
                          count=int(random.random() * 5 + 5),
                          scale=0.8,
                          spread=0.3,
                          chunk_type='spark')

            def _blast(self):
                stdbomb.Blast(
                    position=self.position,
                    velocity=self.target.velocity,
                    blast_radius=2,
                    blast_type='normal',
                    source_player=None,
                    hit_type='punch',
                    hit_subtype='normal').autoretain()

            def _update(self):
                if not self.target:
                    del self  # commit suicide because we have no goal in our existing :(
                    return
                d = ba.Vec3(self.target.position) - ba.Vec3(self.position)

                if d.length() < 0.1:
                    self._blast()
                    del self
                    return

                d = d.normalized() * 0.04

                from math import sin, cos

                self.position = (self.position[0] + d.x + sin(ba.time() * 2) * 0.03,
                                 self.position[1] + d.y,
                                 self.position[2] + d.z + cos(ba.time() * 2) * 0.03)
                self._sparkle()

                ba.timer(0.001, ba.WeakCall(self._update))

        def sparkling(x, y, z):
            Sparkling(position=(x, z, y), target=self.node).autoretain()

        def summon_tnt(x, y, z):
            stdbomb.Bomb(bomb_type='tnt', blast_radius=3, position=(x, z + 4, y), velocity=(0, -10, 0)).autoretain()

        scale = 1
        delta = 0.02

        op = self.node.position
        for i, (x, y) in enumerate(star_positions):
            ba.timer(i * delta, ba.Call(blast, self.node.position[0] + x * scale, self.node.position[2] + y * scale,
                                        self.node.position[1]))
        for i in range(4):
            ba.timer((len(star_positions)) * delta + i * 0.2, ba.Call(summon_tnt, op[0], op[2], op[1]))
        ba.timer((len(star_positions)) * delta + 1.0,
                 ba.Call(sparkling, self.node.position[0], self.node.position[2],
                         self.node.position[1]))

        def last_blast():
            stdbomb.Blast(
                position=self.node.position,
                velocity=(self.node.velocity[0],
                          self.node.velocity[1] + 10,
                          self.node.velocity[2]),
                blast_radius=2,
                blast_type='normal',
                source_player=None,
                hit_type='punch',
                hit_subtype='normal').autoretain()

        # ba.timer(
        #     2 * len(star_positions) * delta + 0.2,
        #     last_blast)

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
