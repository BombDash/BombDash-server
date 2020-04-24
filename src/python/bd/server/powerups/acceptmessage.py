# Copyright (c) 2020 BombDash

import random
import ba
from bastd.actor.popuptext import PopupText
import bastd.actor.spaz as bastd_spaz
from bastd.actor.bomb import Bomb, Blast
from bastd.actor.powerupbox import PowerupBoxFactory, PowerupBox, get_factory

from bd.server.actor.companioncube import CompanionCube


def get_locale(*args, **kwargs):  # TODO: create get_locate function
    pass


ba.app.config['Powerup Popups'] = False  # TODO: remove


def _decorator(f):
    def func(self, msg, *args, **kwargs):
        f(self, msg, *args, **kwargs)
        if isinstance(msg, ba.PowerupMessage):
            if msg.poweruptype == 'speed':
                if ba.app.config.get('Powerup Popups', True):
                    powerup_text = get_locale(
                        'powerup_names')['speed']

                    PopupText(
                        ba.Lstr(translate=('gameDescriptions', powerup_text)),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoretain()

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

            elif msg.poweruptype == 'jump_boost':
                if ba.app.config.get('Powerup Popups', True):
                    powerup_text = get_locale(
                        'powerup_names')['jump_boost']

                    PopupText(
                        ba.Lstr(translate=('gameDescriptions', powerup_text)),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoretain()

                powerup_expiration_time = 20

                def high_jump_wrapper():
                    if not self.node.exists():
                        return

                    t = ba.time()
                    if (t - self.last_jump_time >= self._jump_cooldown
                            and not (self.node.knockout > 0.0
                                     or self.node.frozen > 0)):
                        self.node.jump_pressed = True
                        self.last_jump_time = t
                        self._jump_cooldown = 1
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

            elif msg.poweruptype == 'companion_cube':
                if ba.app.config.get('Powerup Popups', True):
                    powerup_text = get_locale(
                        'powerup_names')['companion_cube']

                    PopupText(
                        ba.Lstr(translate=('gameDescriptions', powerup_text)),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoretain()

                CompanionCube(
                    position=(self.node.position[0],
                              self.node.position[1] + 1,
                              self.node.position[2]),
                    velocity=(0, 10, 0)).autoretain()

            elif msg.poweruptype == 'airstrike_bombs':
                if ba.app.config.get('Powerup Popups', True):
                    powerup_text = get_locale(
                        'powerup_names')['airstrike_bombs']

                    PopupText(
                        ba.Lstr(translate=('gameDescriptions', powerup_text)),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoretain()

                self.set_airstrike_bomb_count(self.airstrike_bomb_count + 1)

            elif msg.poweruptype == 'holy_bombs':
                if ba.app.config.get('Powerup Popups', True):
                    powerup_text = get_locale(
                        'powerup_names')['holy_bombs']

                    PopupText(
                        ba.Lstr(translate=('gameDescriptions', powerup_text)),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoretain()

                self.set_holy_bomb_count(self.holy_bomb_count + 1)

            elif msg.poweruptype == 'elon_mines':
                if ba.app.config.get('Powerup Popups', True):
                    powerup_text = get_locale(
                        'powerup_names')['elon_mines']

                    PopupText(
                        ba.Lstr(translate=('gameDescriptions', powerup_text)),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoretain()

                self.set_elon_mine_count(self.elon_mine_count + 1)

            elif msg.poweruptype == 'portal_bombs':
                if ba.app.config.get('Powerup Popups', True):
                    powerup_text = get_locale(
                        'powerup_names')['portal_bombs']

                    PopupText(
                        ba.Lstr(translate=('gameDescriptions', powerup_text)),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoretain()

                self.set_portal_bomb_count(self.portal_bomb_count + 1)

            elif msg.poweruptype == 'sticky_gift_bomb':
                if ba.app.config.get('Powerup Popups', True):
                    powerup_text = get_locale(
                        'powerup_names')['sticky_gift']

                    PopupText(
                        ba.Lstr(translate=('gameDescriptions', powerup_text)),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoretain()

                self.set_sticky_gift_bomb_count(self.sticky_gift_bomb_count + 1)

            elif msg.poweruptype == 'heal_bombs':
                if ba.app.config.get('Powerup Popups', True):
                    powerup_text = get_locale(
                        'powerup_names')['heal_bombs']

                    PopupText(
                        ba.Lstr(translate=('gameDescriptions', powerup_text)),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoretain()

                self.set_health_bomb_count(self.health_bomb_count + 1)

            elif msg.poweruptype == 'lucky_block':
                event_number = random.randint(1, 15)
                if event_number not in (1, 2, 3, 4):
                    if ba.app.config.get('Powerup Popups', True):
                        powerup_text = get_locale(
                            'powerup_names')['lucky_block']

                        PopupText(
                            ba.Lstr(translate=('gameDescriptions',
                                               powerup_text)),
                            color=(1, 1, 1),
                            scale=1,
                            position=self.node.position).autoretain()

                if event_number in (1, 2, 3):
                    powerup_type = PowerupBoxFactory(
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

                    powerup_type = PowerupBoxFactory().get_random_powerup_type()

                    PowerupBox(
                        position=(self.node.position[0],
                                  self.node.position[1] + 4,
                                  self.node.position[2]),
                        poweruptype=powerup_type,
                        expire=True).autoretain()

                    powerup_type = PowerupBoxFactory(
                    ).get_random_powerup_type()

                    PowerupBox(
                        position=(self.node.position[0],
                                  self.node.position[1] + 4,
                                  self.node.position[2]),
                        poweruptype=powerup_type,
                        expire=True).autoretain()

                    powerup_type = PowerupBoxFactory(
                    ).get_random_powerup_type()

                    PowerupBox(
                        position=(self.node.position[0],
                                  self.node.position[1] + 4,
                                  self.node.position[2]),
                        poweruptype=powerup_type,
                        expire=True).autoretain()
                elif event_number == 5:
                    big_bomb = Bomb(
                        position=(self.node.position[0],
                                  self.node.position[1] + 3,
                                  self.node.position[2]),
                        source_player=self.sourcePlayer,
                        owner=self.node,
                        blast_radius=6)

                    def change_scale_wrapper():
                        if big_bomb.node.exists():
                            big_bomb.node.modelScale = 3

                    ba.timer(300, change_scale_wrapper)

                    def boom_wrapper():
                        if big_bomb.node.exists():
                            position = big_bomb.node.position
                            Blast(blast_type='giant',
                                  position=position,
                                  blast_radius=6)

                            Blast(blast_type='normal',
                                  position=position,
                                  blast_radius=10)

                    ba.timer(2000, boom_wrapper)
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
                    ba.setmusic(ba.MusicType('corkPop'))  # position=self.node.position?
                elif event_number == 8:
                    position = self.node.position

                    def rain_wrapper():
                        powerup_type = PowerupBoxFactory().get_random_powerup_type()

                        new_position = (
                            -10 + position[0] + random.random() * 20,
                            position[1] + 6,
                            -10 + position[2] + random.random() * 20
                        )

                        PowerupBox(poweruptype=powerup_type,
                                   position=new_position).autoretain()

                        if random.random() > 0.04:
                            ba.timer(100, rain_wrapper)

                    rain_wrapper()
                elif event_number == 9:
                    Blast(position=self.node.position,
                          velocity=self.node.velocity,
                          blast_radius=1.0,
                          blast_type='normal',
                          source_player=None,
                          hit_type='punch',
                          hit_subtype='normal')
                elif event_number == 10:
                    x = self.node.position[0] - 2
                    while x < self.node.position[0] + 2:
                        y = self.node.position[2] - 2
                        while y < self.node.position[2] + 2:
                            Blast(
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
                    while offset < 15:
                        velocity = (12 + random.random() * 8, -0.1, 0)
                        Bomb(bomb_type='tnt',
                             position=(-10, 6, offset),
                             velocity=velocity).autoretain()

                        offset += 1.5
                elif event_number == 12:
                    color = {
                        0: (0, 0, 3),
                        500: (0, 3, 0),
                        1000: (3, 0, 0),
                        1500: (0, 0, 3)
                    }

                    ba.animate_array(self.node, 'color', 3, color, True)
                    self.node.handlemessage('celebrate', 100000000)
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

    return func


def _decorator_init(f):
    def func(self, *args, **kwargs):
        f(self, *args, **kwargs)
        self.sticky_gift_bomb_count = 0
        self.portal_bomb_count = 0
        self.health_bomb_count = 0
        self.airstrike_bomb_count = 0
        self.elon_mine_count = 0
        self.holy_bomb_count = 0

        self.last_jump_time = 0
        self._jump_cooldown = 1

    return func


def set_sticky_gift_bomb_count(self, count):
    """
    Set the number of sticky gift bombs this spaz is carrying.
    """
    self.sticky_gift_bomb_count = count
    if self.node.exists():
        if self.sticky_gift_bomb_count != 0:
            self.node.counter_text = 'x' + str(self.sticky_gift_bomb_count)
            self.node.counter_texture = get_factory().tex_sticky_gift_bomb
        else:
            self.node.counter_text = ''


def set_health_bomb_count(self, count):
    """
    Set the number of health bombs this spaz is carrying.
    """
    self.health_bomb_count = count
    if self.node.exists():
        if self.health_bomb_count != 0:
            self.node.counter_text = 'x' + str(self.health_bomb_count)
            self.node.counter_texture = get_factory().tex_health_bomb
        else:
            self.node.counter_text = ''


def set_airstrike_bomb_count(self, count):
    """
    Set the number of airstrike bombs this spaz is carrying.
    """
    self.airstrike_bomb_count = count
    if self.node.exists():
        if self.airstrike_bomb_count != 0:
            self.node.counter_text = 'x' + str(self.airstrike_bomb_count)
            self.node.counter_texture = get_factory().tex_airstrike_bomb
        else:
            self.node.counter_text = ''


def set_elon_mine_count(self, count):
    """
    Set the number of elon-mines this spaz is carrying.
    """
    self.elon_mine_count = count
    if self.node.exists():
        if self.elon_mine_count != 0:
            self.node.counter_text = 'x' + str(self.elon_mine_count)
            self.node.counter_texture = get_factory().tex_elon_musk_mine
        else:
            self.node.counter_text = ''


def set_portal_bomb_count(self, count):
    """
    Set the number of portal bombs this spaz is carrying.
    """
    self.portal_bomb_count = count
    if self.node.exists():
        if self.portal_bomb_count != 0:
            self.node.counter_text = 'x' + str(self.portal_bomb_count)
            self.node.counter_texture = get_factory().tex_portal_bomb
        else:
            self.node.counter_text = ''


def set_holy_bomb_count(self, count):
    """
    Set the number of holy bombs this spaz is carrying.
    """
    self.holy_bomb_count = count
    if self.node.exists():
        if self.holy_bomb_count != 0:
            self.node.counter_text = 'x' + str(self.holy_bomb_count)
            self.node.counter_texture = get_factory().tex_holy_bomb
        else:
            self.node.counter_text = ''


bastd_spaz.Spaz.__init__ = _decorator_init(bastd_spaz.Spaz.__init__)
bastd_spaz.Spaz.handlemessage = _decorator(bastd_spaz.Spaz.handlemessage)
bastd_spaz.Spaz.set_sticky_gift_bomb_count = set_sticky_gift_bomb_count
bastd_spaz.Spaz.set_portal_bomb_count = set_portal_bomb_count
bastd_spaz.Spaz.set_health_bomb_count = set_health_bomb_count
bastd_spaz.Spaz.set_airstrike_bomb_count = set_airstrike_bomb_count
bastd_spaz.Spaz.set_elon_mine_count = set_elon_mine_count
bastd_spaz.Spaz.set_holy_bomb_count = set_holy_bomb_count
