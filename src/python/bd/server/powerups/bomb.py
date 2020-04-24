# Copyright (c) 2020 BombDash

import ba
import bastd.actor.bomb as stdbomb
from bastd.actor.bomb import ExplodeMessage, get_factory, WarnMessage, ArmMessage, ImpactMessage


class SetStickyMessage:
    pass


def _bomb_init(self,
               position=(0.0, 1.0, 0.0),
               velocity=(0.0, 0.0, 0.0),
               bomb_type: str = 'normal',
               blast_radius: float = 2.0,
               source_player: ba.Player = None,
               owner: ba.Node = None):
    """Create a new Bomb.

    bomb_type can be 'ice','impact','land_mine','normal','sticky', or
    'tnt'. Note that for impact or land_mine bombs you have to call arm()
    before they will go off.
    """
    ba.Actor.__init__(self)

    factory = get_factory()

    if bomb_type not in ('ice', 'impact', 'land_mine', 'normal', 'sticky',
                         'tnt', 'sticky_gift', 'health', 'portal', 'holy',
                         'airstrike', 'elon_mine'):
        raise Exception("invalid bomb type: " + bomb_type)
    self.bomb_type = bomb_type

    self._exploded = False

    self.texture_sequence = None

    if self.bomb_type == 'sticky':
        self._last_sticky_sound_time = 0.0

    self.blast_radius = blast_radius
    if self.bomb_type == 'ice':
        self.blast_radius *= 1.2
    elif self.bomb_type == 'impact':
        self.blast_radius *= 0.7
    elif self.bomb_type == 'land_mine':
        self.blast_radius *= 0.7
    elif self.bomb_type == 'tnt':
        self.blast_radius *= 1.45
    elif self.bomb_type == 'elon_mine':
        self.blast_radius *= 0.7
    elif self.bomb_type == 'holy':
        self.blast_radius *= 1.45
    elif self.bomb_type == 'sticky_gift':
        self.blast_radius *= 0.3

    self._explode_callbacks = []

    # the player this came from
    self.source_player = source_player

    # by default our hit type/subtype is our own, but we pick up types of
    # whoever sets us off so we know what caused a chain reaction
    self.hit_type = 'explosion'
    self.hit_subtype = self.bomb_type

    # if no owner was provided, use an unconnected node ref
    # (nevermind; trying to use None in these type cases instead)
    # if owner is None:
    #     owner = ba.Node(None)

    # the node this came from
    self.owner = owner

    # adding footing-materials to things can screw up jumping and flying
    # since players carrying those things
    # and thus touching footing objects will think they're on solid
    # ground.. perhaps we don't wanna add this even in the tnt case?..
    materials: tuple
    if self.bomb_type == 'tnt':
        materials = (factory.bomb_material,
                     ba.sharedobj('footing_material'),
                     ba.sharedobj('object_material'))
    else:
        materials = (factory.bomb_material,
                     ba.sharedobj('object_material'))

    if self.bomb_type in ('impact', 'health', 'portal', 'holy', 'airstrike'):
        materials = materials + (factory.impact_blast_material,)
    elif self.bomb_type in ('land_mine', 'elon_mine'):
        materials = materials + (factory.land_mine_no_explode_material,)
    elif self.bomb_type == 'sticky_gift':
        materials = materials + (factory.sticky_gift_material,)

    if self.bomb_type == 'sticky':
        materials = materials + (factory.sticky_material,)
    else:
        materials = materials + (factory.normal_sound_material,)

    fuse_time = None

    if self.bomb_type == 'health':
        self.node = ba.newnode('prop', delegate=self, attrs={
            'body': 'sphere',
            'position': position,
            'velocity': velocity,
            'materials': materials})

        self.first_shield = ba.newnode(
            'shield', owner=self.node, attrs={
                'color': (1, 1, 1),
                'radius': 0.6})

        self.node.connectattr(
            'position', self.first_shield, 'position')

        self.second_shield = ba.newnode(
            'shield', owner=self.node, attrs={
                'color': (20, 0, 0),
                'radius': 0.4})

        self.node.connectattr(
            'position', self.second_shield, 'position')

        ba.animate(self.second_shield, 'radius',
                   {0: 0.1, 0.3: 0.5, 0.6: 0.1}, True)

    elif self.bomb_type == 'portal':
        self.node = ba.newnode('prop', delegate=self, attrs={
            'body': 'sphere',
            'bodyScale': 0.85,
            'position': position,
            'velocity': velocity,
            'materials': materials})

        self.first_shield = ba.newnode(
            'shield', owner=self.node, attrs={
                'color': (1, 1, 1),
                'radius': 0.6})

        self.node.connectattr(
            'position', self.first_shield, 'position')

        self.second_shield = ba.newnode(
            'shield', owner=self.node, attrs={
                'color': (0, 0, 20),
                'radius': 0.4})

        self.node.connectattr(
            'position', self.second_shield, 'position')

        color = {
            0: (1, 1, 1),
            1: (20, 0, 0),
            2: (20, 10, 0),
            3: (20, 20, 0),
            4: (0, 20, 0),
            5: (0, 10, 20),
            6: (0, 0, 20),
            7: (10, 0, 20),
            8: (1, 1, 1)
        }

        ba.animate_array(self.second_shield, 'color',
                         3, color, True)

    elif self.bomb_type == 'elon_mine':
        self.node = ba.newnode('prop', delegate=self, attrs={
            'body': 'landMine',
            'model': factory.land_mine_model,
            'light_model': factory.land_mine_model,
            'color_texture': factory.elon_mine_tex,
            'position': position,
            'velocity': velocity,
            'shadow_size': 0.44,
            'reflection': 'powerup',
            'reflection_scale': [1],
            'materials': materials})

    elif self.bomb_type == 'airstrike':
        self.node = ba.newnode('prop', delegate=self, attrs={
            'body': 'sphere',
            'model': factory.impact_bomb_model,
            'color_texture': factory.airstrike_tex,
            'position': position,
            'velocity': velocity,
            'shadow_size': 0.3,
            'reflection': 'powerup',
            'reflection_scale': [1.5],
            'materials': materials})

    elif self.bomb_type == 'holy':
        self.node = ba.newnode('prop', delegate=self, attrs={
            'body': 'sphere',
            'model': factory.bomb_model,
            'light_model': factory.bomb_model,
            'color_texture': factory.holy_tex,
            'position': position,
            'velocity': velocity,
            'shadow_size': 0.5,
            'reflection': 'powerup',
            'reflection_scale': [1],
            'materials': materials})

    elif self.bomb_type == 'sticky_gift':
        self.node = ba.newnode(
            'prop', delegate=self, owner=owner, attrs={
                'body': 'sphere',
                'model': factory.sticky_bomb_model,
                'light_model': factory.sticky_bomb_model,
                'color_texture': factory.sticky_gift_tex,
                'position': position,
                'velocity': velocity,
                'shadow_size': 0.44,
                'reflection': 'powerup',
                'reflection_scale': [1],
                'materials': materials})

    elif self.bomb_type == 'land_mine':
        fuse_time = None
        self.node = ba.newnode('prop',
                               delegate=self,
                               attrs={
                                   'position': position,
                                   'velocity': velocity,
                                   'model': factory.land_mine_model,
                                   'light_model': factory.land_mine_model,
                                   'body': 'landMine',
                                   'shadow_size': 0.44,
                                   'color_texture': factory.land_mine_tex,
                                   'reflection': 'powerup',
                                   'reflection_scale': [1.0],
                                   'materials': materials
                               })

    elif self.bomb_type == 'tnt':
        fuse_time = None
        self.node = ba.newnode('prop',
                               delegate=self,
                               attrs={
                                   'position': position,
                                   'velocity': velocity,
                                   'model': factory.tnt_model,
                                   'light_model': factory.tnt_model,
                                   'body': 'crate',
                                   'shadow_size': 0.5,
                                   'color_texture': factory.tnt_tex,
                                   'reflection': 'soft',
                                   'reflection_scale': [0.23],
                                   'materials': materials
                               })

    elif self.bomb_type == 'impact':
        fuse_time = 20.0
        self.node = ba.newnode('prop',
                               delegate=self,
                               attrs={
                                   'position': position,
                                   'velocity': velocity,
                                   'body': 'sphere',
                                   'model': factory.impact_bomb_model,
                                   'shadow_size': 0.3,
                                   'color_texture': factory.impact_tex,
                                   'reflection': 'powerup',
                                   'reflection_scale': [1.5],
                                   'materials': materials
                               })
        self.arm_timer = ba.Timer(
            0.2, ba.WeakCall(self.handlemessage, ArmMessage()))
        self.warn_timer = ba.Timer(
            fuse_time - 1.7, ba.WeakCall(self.handlemessage,
                                         WarnMessage()))

    else:
        fuse_time = 3.0
        if self.bomb_type == 'sticky':
            sticky = True
            model = factory.sticky_bomb_model
            rtype = 'sharper'
            rscale = 1.8
        else:
            sticky = False
            model = factory.bomb_model
            rtype = 'sharper'
            rscale = 1.8
        if self.bomb_type == 'ice':
            tex = factory.ice_tex
        elif self.bomb_type == 'sticky':
            tex = factory.sticky_tex
        else:
            tex = factory.regular_tex
        self.node = ba.newnode('bomb',
                               delegate=self,
                               attrs={
                                   'position': position,
                                   'velocity': velocity,
                                   'model': model,
                                   'shadow_size': 0.3,
                                   'color_texture': tex,
                                   'sticky': sticky,
                                   'owner': owner,
                                   'reflection': rtype,
                                   'reflection_scale': [rscale],
                                   'materials': materials
                               })

        sound = ba.newnode('sound',
                           owner=self.node,
                           attrs={
                               'sound': factory.fuse_sound,
                               'volume': 0.25
                           })
        self.node.connectattr('position', sound, 'position')
        ba.animate(self.node, 'fuse_length', {0.0: 1.0, fuse_time: 0.0})

    # Light the fuse!!!
    if self.bomb_type not in ('land_mine', 'tnt', 'sticky_gift', 'health', 'portal', 'holy',
                              'airstrike', 'elon_mine'):
        assert fuse_time is not None
        ba.timer(fuse_time,
                 ba.WeakCall(self.handlemessage, ExplodeMessage()))

    ba.animate(self.node, "model_scale", {0: 0, 0.2: 1.3, 0.26: 1})


def bomb_handle_impact(self):
    node = ba.get_collision_info("opposing_node")
    # if we're an impact bomb and we came from this node, don't explode...
    # alternately if we're hitting another impact-bomb from the same
    # source, don't explode...
    try:
        node_delegate = node.getdelegate()
    except Exception:
        node_delegate = None
    if node:
        if (self.bomb_type in ('impact', 'holy', 'health', 'portal', 'airstrike')
                and (node is self.owner or
                     (isinstance(node_delegate, stdbomb.Bomb)
                      and node_delegate.bomb_type in ('impact', 'holy', 'health', 'portal', 'airstrike')
                      and node_delegate.owner is self.owner))):
            return
        self.handlemessage(ExplodeMessage())


def _decorator_factory(f):
    def func(self, *args, **kwargs):
        f(self, *args, **kwargs)
        self.holy_tex = ba.gettexture('aliColor')
        self.sticky_gift_tex = ba.gettexture('egg2')
        self.airstrike_tex = ba.gettexture('ouyaAButton')
        self.elon_mine_tex = ba.gettexture('achievementCrossHair')
        self.elon_mine_lit_tex = ba.gettexture('circleNoAlpha')

        self.land_mine_no_explode_material = ba.Material()
        self.land_mine_blast_material = ba.Material()
        self.land_mine_blast_material.add_actions(
            conditions=(
                ('we_are_older_than', 200),
                'and', ('they_are_older_than', 200),
                'and', ('eval_colliding',),
                'and', (('they_dont_have_material',
                         self.land_mine_no_explode_material),
                        'and', (('they_have_material',
                                 ba.sharedobj('object_material')),
                                'or', ('they_have_material',
                                       ba.sharedobj('player_material'))))),
            actions=('message', 'our_node', 'at_connect', ImpactMessage()))

        self.sticky_gift_material = ba.Material()
        self.sticky_gift_material.add_actions(
            conditions=(('we_are_older_than', 200), 'and',
                        ('they_are_older_than', 200), 'and',
                        ('eval_colliding',), 'and',
                        (('they_dont_have_material',
                          self.land_mine_no_explode_material), 'and',
                         (('they_have_material',
                           ba.sharedobj('object_material')), 'or',
                          ('they_have_material',
                           ba.sharedobj('player_material'))))),
            actions=(('message', 'our_node',
                      'at_connect', SetStickyMessage())))

    return func


stdbomb.BombFactory.__init__ = _decorator_factory(stdbomb.BombFactory.__init__)
stdbomb.Bomb.__init__ = _bomb_init
stdbomb.Bomb._handle_impact = bomb_handle_impact

