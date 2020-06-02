import ba
from _ba import chatmessage
import _ba

from bd.chat.commands_engine import servercommand, _handlers
from bd.playerdata import PlayerData, Status, get_player_by
from bd.locale import get_locale


@servercommand('help'.split(), {Status.ADMIN: 0, Status.VIP: 0})
def help_callback(playerdata: PlayerData, args):
    for handler in _handlers:
        chatmessage("{} - {}".format(
            handler.commands[0],
            get_locale('command_help').get(
                handler.commands[0],
                get_locale('command_help_not_found'))))


@servercommand('list l'.split(), {Status.ADMIN: 0, Status.VIP: 0})
def list_callback(playerdata: PlayerData, args):
    client_ids = [(
        i['players'][0]['name_full'] if i['players'] else
        i['displayString'], str(i['client_id']))
        for i in _ba.get_game_roster()]

    chatmessage(get_locale('player_ids_text'))
    activity = _ba.get_foreground_host_activity()
    for i in range(len(activity.players)):
        p = activity.players[i]
        chatmessage('{} | {} | {}'.format(i, p.getname().ljust(15), p.sessionplayer.inputdevice.client_id))
    chatmessage(get_locale('dividing_strip_text'))


@servercommand('kick'.split(), {Status.ADMIN: 0, Status.VIP: 60})
def kick_callback(playerdata: PlayerData, args):
    if len(args) < 2 or (not args[1].isdigit() and args[1] != '-1'):
        chatmessage(get_locale('chat_command_not_args_error'))
    elif args[1] == '-1':
        chatmessage(get_locale('kick_host_error'))
    else:
        ban_time = 300
        clients_ids = [player['client_id'] for player in
                       _ba.get_game_roster()]
        if len(args) > 1 and playerdata.status == Status.ADMIN:
            ban_time = int(args[1])
        elif len(args) > 1 and playerdata.status != Status.ADMIN:
            chatmessage(get_locale('time_arg_access_error'))

        if int(args[1]) in clients_ids:
            target = get_player_by('client_id', int(args[1]))
            if target.status == Status.ADMIN:
                chatmessage(get_locale('kick_admin_error'))
            else:
                _ba.disconnect_client(int(args[1]),
                                      ban_time=ban_time)
        else:
            chatmessage(get_locale('not_player_error'))


@servercommand('remove'.split(), {Status.ADMIN: 0, Status.VIP: 60})
def remove_callback(playerdata: PlayerData, args):
    activity = ba.getactivity()
    if len(args) < 2:
        chatmessage(get_locale('chat_command_not_args_error'))
    elif args[1] == 'all' and playerdata.status == Status.ADMIN:
        for player in activity.players:
            player.sessionplayer.remove_from_game()
    else:
        activity.players[int(args[1])].sessionplayer.remove_from_game()


@servercommand('end'.split(), {Status.ADMIN: 0, Status.VIP: 120})
def end_callback(playerdata: PlayerData, args):
    activity = ba.getactivity()
    assert isinstance(activity, ba.GameActivity)
    activity.end_game()


@servercommand('ooh'.split(), {Status.ADMIN: 0, Status.VIP: 60})
def ooh_callback(playerdata: PlayerData, args):
    ba.playsound(ba.getsound('ooh'), volume=2)


@servercommand('playsound ps'.split(), {Status.ADMIN: 0, Status.VIP: 0})
def play_sound_callback(playerdata: PlayerData, args):
    if len(args) < 2:
        chatmessage(get_locale('chat_command_not_args_error'))
    else:
        ba.playsound(ba.getsound(str(args[0])), volume=2)


@servercommand('nv'.split(), {Status.ADMIN: 0, Status.VIP: 0})
def nv_callback(playerdata: PlayerData, args):
    activity = ba.getactivity()
    tint = {0: activity.globalsnode.tint,
            1: (0.5, 0.7, 1.0)}
    ba.animate_array(activity.globalsnode, 'tint', 3, tint)


@servercommand('dv'.split(), {Status.ADMIN: 0, Status.VIP: 0})
def dv_callback(playerdata: PlayerData, args):
    tint = {0: ba.getactivity().globalsnode.tint,
            1: (1.0, 1.0, 1.0)}

    ba.animate_array(ba.getactivity().globalsnode, 'tint', 3, tint)


@servercommand('box tnt'.split(), {Status.ADMIN: 0, Status.VIP: 0})
def box_callback(playerdata: PlayerData, args):
    from bastd.actor.playerspaz import PlayerSpaz

    def do_box(player):
        if player.actor and isinstance(player.actor, PlayerSpaz) and player.actor.node:
            player.actor.node.torso_model = ba.getmodel('tnt')
            player.actor.node.color_mask_texture = ba.gettexture('tnt')
            player.actor.node.color_texture = ba.gettexture('tnt')
            player.actor.node.highlight = (1, 1, 1)
            player.actor.node.color = (1, 1, 1)
            player.actor.node.head_model = None
            player.actor.node.style = 'cyborg'

    activity = ba.getactivity()
    if len(args) < 2:
        chatmessage(get_locale('chat_command_not_args_error'))
    elif args[1] == 'all' and playerdata.status == Status.ADMIN:
        for iplayer in activity.players:
            do_box(iplayer)
    else:
        try:
            iplayer = activity.players[int(args[1])]
            do_box(iplayer)
        except (IndexError, ValueError):
            chatmessage(get_locale('not_player_error'))


@servercommand('hug'.split(), {Status.VIP: 10, Status.ADMIN: 0})
def hug_callback(playerdata: PlayerData, args):
    def do_hug(p1: ba.Player, p2: ba.Player):
        from bastd.actor.playerspaz import PlayerSpaz
        if (p1.actor.is_alive() and isinstance(p1.actor, PlayerSpaz) and
                p2.actor.is_alive() and isinstance(p2.actor, PlayerSpaz)):
            p1.actor.node.hold_node = p2.actor.node
            p2.actor.node.hold_node = p1.actor.node

    activity = ba.getactivity()
    if len(args) == 1:
        alives = []
        for i in range(len(activity.players)):
            if activity.players[i]:
                alives.append(i)
        count = len(alives) // 2
        for i in range(count):
            do_hug(activity.players[alives[i]], activity.players[alives[count + i]])
    elif len(args) == 3:
        try:
            do_hug(activity.players[int(args[1])], activity.players[int(args[2])])
        except (IndexError, ValueError):
            chatmessage(get_locale('not_player_error'))


@servercommand('tint'.split(), {Status.VIP: 0, Status.ADMIN: 0})
def tint_callback(playerdata: PlayerData, args):
    if len(args) < 2 or (len(args) < 4 and args[1] != 'r'):
        chatmessage(get_locale('chat_command_not_args_error'))
    elif args[1] == 'r':
        m = 1.30 if len(args) < 3 else float(args[2])
        s = 1000 if len(args) < 4 else float(args[3])
        if m > 3 and playerdata.status != Status.ADMIN:
            chatmessage(get_locale('too_big_arg_error'))
            return
        tint = {
            s * 0: (m, 0, 0),
            s * 1: (0, m, 0),
            s * 2: (0, 0, m),
            s * 3: (m, 0, 0),
        }

        ba.animate_array(ba.getactivity().globalsnode,
                         'tint', 3, tint, True, suppress_format_warning=True,
                         timeformat=ba.TimeFormat.MILLISECONDS)
    else:
        color = (float(args[1]),
                 float(args[2]),
                 float(args[3]))
        if max(map(abs, color)) > 3 and playerdata.status != Status.ADMIN:
            chatmessage(get_locale('too_big_arg_error'))
            return
        ba.getactivity().globalsnode.tint = color


@servercommand('sm'.split(), {Status.ADMIN: 0, Status.VIP: 0})
def sm_callback(playerdata: PlayerData, args):
    if not ba.getactivity().globalsnode.slow_motion:
        ba.getactivity().globalsnode.slow_motion = True
    else:
        ba.getactivity().globalsnode.slow_motion = False


@servercommand('gp'.split(), {Status.VIP: 0, Status.ADMIN: 0})
def gp_callback(playerdata: PlayerData, args):
    activity = ba.getactivity()
    if len(args) < 2:
        chatmessage(get_locale('chat_command_not_args_error'))
    else:
        chatmessage(get_locale('player_profiles_text'))
        try:
            inputdevice = activity.players[int(args[1])].sessionplayer.inputdevice
        except (IndexError, ValueError):
            chatmessage(get_locale('not_player_error'))
            return
        profiles = inputdevice.get_player_profiles()

        for profile in profiles:
            if profile == '__account__':
                profile = inputdevice.get_account_name(False)
            chatmessage(profile)

        chatmessage(get_locale('dividing_strip_text'))


@servercommand('fly'.split(), {Status.VIP: 60, Status.ADMIN: 0})
def fly_callback(playerdata: PlayerData, args):
    from bastd.actor.playerspaz import PlayerSpaz
    activity = ba.getactivity()
    if not args:
        chatmessage(get_locale('chat_command_not_args_error'))
    elif args[1] == 'all' and playerdata.status == Status.ADMIN:
        for player in activity.players:
            if player.actor and isinstance(player.actor, PlayerSpaz):
                player.actor.node.fly = True
    else:
        try:
            player = activity.players[int(args[1])]
        except (IndexError, ValueError):
            chatmessage(get_locale('not_player_error'))
            return
        if player.actor and hasattr(player.actor, 'node'):
            if not player.actor.node.fly:
                player.actor.node.fly = True
            else:
                player.actor.node.fly = False


@servercommand('ac'.split(), {Status.ADMIN: 0, Status.VIP: 0})
def ac_callback(playerdata: PlayerData, args):
    if not args:
        chatmessage(get_locale('chat_command_not_args_error'))
    elif args[1] == 'r':
        m = 1.30 if len(args) < 3 else float(args[2])
        s = 1000 if len(args) < 4 else float(args[3])
        ambient_color = {
            s * 0: (m, 0, 0),
            s * 1: (0, m, 0),
            s * 2: (0, 0, m),
            s * 3: (m, 0, 0)
        }

        ba.animate_array(ba.getactivity().globalsnode,
                         'ambient_color', 3, ambient_color, True, suppress_format_warning=True,
                         timeformat=ba.TimeFormat.MILLISECONDS)
    else:
        ba.getactivity().globalsnode.ambientColor = (float(args[1]),
                                                     float(args[2]),
                                                     float(args[3]))


@servercommand('io iceoff'.split(), statuses={Status.ADMIN: 0, Status.VIP: 0})
def ice_off_callback(playerdata: PlayerData, args):
    from bastd.gameutils import SharedObjects
    shared = SharedObjects.get()
    activity = ba.getactivity()
    assert isinstance(activity, ba.GameActivity)
    activity.map.is_hockey = False
    activity.map.node.materials = [shared.footing_material]
    activity.map.floor.materials = [shared.footing_material]


@servercommand('heal'.split(), {Status.VIP: 10, Status.ADMIN: 0})
def heal_callback(playerdata: PlayerData, args):
    activity = ba.getactivity()
    if len(args) < 2:
        chatmessage(get_locale('chat_command_not_args_error'))
    elif args[1] == 'all':
        for i in activity.players:
            if i.actor and hasattr(i.actor, 'node'):
                assert isinstance(i.actor.node, ba.Node)
                i.actor.node.handlemessage(
                    ba.PowerupMessage(poweruptype='health'))
    else:
        player = activity.players[int(args[0])]
        if player.actor and hasattr(player.actor, 'node'):
            assert isinstance(player.actor.node, ba.Node)
            player.actor.node.handlemessage(
                ba.PowerupMessage(poweruptype='health'))


@servercommand('ref reflections'.split(), {Status.VIP: 0, Status.ADMIN: 0})
def reflections_callback(playerdata: PlayerData, args):
    activity = ba.getactivity()
    assert isinstance(activity, ba.GameActivity)
    try:
        rs = [int(args[2])]
        ref_type = 'soft' if int(args[1]) == 0 else 'powerup'
    except (ValueError, IndexError):
        chatmessage(get_locale('chat_command_not_args_error'))
        return

    activity.map.node.reflection = ref_type
    activity.map.node.reflection_scale = rs

    try:
        activity.map.bg.reflection = ref_type
        activity.map.bg.reflection_scale = rs
    except AttributeError:
        pass

    try:
        activity.map.floor.reflection = ref_type
        activity.map.floor.reflection_scale = rs
    except AttributeError:
        pass

    try:
        activity.map.center.reflection = ref_type
        activity.map.center.reflection_scale = rs
    except AttributeError:
        pass


@servercommand('shatter'.split(), {Status.VIP: 10, Status.ADMIN: 0})
def shatter_callback(playerdata: PlayerData, args):
    activity = ba.getactivity()
    if len(args) < 3 or not args[2].isdigit():
        chatmessage(get_locale('chat_command_not_args_error'))
    else:
        level = int(args[2])
        if args[1] == 'all' and playerdata.status == Status.ADMIN:
            for i in activity.players:
                i.actor.node.shattered = level
        else:
            try:
                activity.players[int(args[0])].actor.node.shattered = level
            except (ValueError, IndexError):
                chatmessage(get_locale('not_player_error'))

# ВНИМАНИЕ! ЗАКРОЙТЕ ГЛАЗА! тут говнокод
# @servercommand(commands=('/cm',),
#                                 statuses=(Status.VIP, Status.ADMIN))
# def cm_callback(playerdata: PlayerData, args):
#     if not args:
#         time = 10000
#     else:
#         time = int(args[0])
#
#     op = 0.08
#     std = ba.getactivity().globalsnode.vignetteOuter
#     vignetteOuter = {
#         0: ba.getactivity().globalsnode.vignetteOuter,
#         17000: (0, 1, 0)
#     }
#
#     ba.animateArray(ba.getactivity().globalsnode,
#                     'vignetteOuter', 3, vignetteOuter)
#
#     try:
#         activity.map.node.opacity = op
#     except Exception:
#         pass
#
#     try:
#         activity.map.bg.opacity = op
#     except Exception:
#         pass
#
#     try:
#         activity.map.bg.node.opacity = op
#     except Exception:
#         pass
#
#     try:
#         activity.map.node1.opacity = op
#     except Exception:
#         pass
#
#     try:
#         activity.map.node2.opacity = op
#     except Exception:
#         pass
#
#     try:
#         activity.map.node3.opacity = op
#     except Exception:
#         pass
#
#     try:
#         activity.map.steps.opacity = op
#     except Exception:
#         pass
#
#     try:
#         activity.map.floor.opacity = op
#     except Exception:
#         pass
#
#     try:
#         activity.map.node4.opacity = op
#     except Exception:
#         pass
#
#     try:
#         activity.map.center.opacity = op
#     except Exception:
#         pass
#
#     def off():
#         op = 1
#         try:
#             activity.map.node.opacity = op
#         except Exception:
#             pass
#
#         try:
#             activity.map.bg.opacity = op
#         except Exception:
#             pass
#
#         try:
#             activity.map.bg.node.opacity = op
#         except Exception:
#             pass
#
#         try:
#             activity.map.node1.opacity = op
#         except Exception:
#             pass
#
#         try:
#             activity.map.node2.opacity = op
#         except Exception:
#             pass
#
#         try:
#             activity.map.node3.opacity = op
#         except Exception:
#             pass
#
#         try:
#             activity.map.node4.opacity = op
#         except Exception:
#             pass
#
#         try:
#             activity.map.steps.opacity = op
#         except Exception:
#             pass
#
#         try:
#             activity.map.floor.opacity = op
#         except Exception:
#             pass
#
#         try:
#             activity.map.center.opacity = op
#         except Exception:
#             pass
#
#         vignetteOuter = {
#             0: ba.getactivity().globalsnode.vignetteOuter,
#             100: std
#         }
#
#         ba.animateArray(ba.getactivity().globalsnode,
#                         'vignetteOuter', 3, vignetteOuter)
#
#     ba.timer(time, off)


@servercommand('sleep'.split(), {Status.VIP: 10, Status.ADMIN: 0})
def sleep_callback(playerdata: PlayerData, args):
    activity = ba.getactivity()
    if not args:
        chatmessage(get_locale('chat_command_not_args_error'))
    elif args[1] == 'all' and playerdata.status == Status.ADMIN:
        for i in activity.players:
            try:
                i.actor.node.handlemessage('knockout', 5000)
            except AttributeError:
                pass
    else:
        try:
            activity.players[int(args[1])].actor.node.handlemessage(
                'knockout', 5000)
        except (ValueError, IndexError):
            chatmessage(get_locale('not_player_error'))
        except AttributeError:
            pass


# @servercommand(commands=('/skin',),
#                                 statuses=(Status.VIP, Status.ADMIN))
# def skin_callback(playerdata: PlayerData, args):
#     if not args:
#         chatmessage(get_locale('chat_command_not_args_error'))
#     elif args[0] == 'names':
#         chatmessage(get_locale('skin_names_text'))
#         for msg in get_locale('skin_names'):
#             chatmessage(msg)
#         chatmessage(get_locale('dividing_strip_text'))
#     elif str(args[1]) in SKIN_NAMES:
#         account_id = activity.players[int(args[0])].get_account_id()
#         bd.server.custom_skins[account_id] = str(args[1])
#     elif str(args[1]) == 'reset':
#         account_id = activity.players[int(args[0])].get_account_id()
#         bd.server.custom_skins.pop(account_id, None)


@servercommand('rainbow'.split(), {Status.VIP: 0, Status.ADMIN: 0})
def rainbow_callback(playerdata: PlayerData, args):
    color = {
        0: (0, 0, 3), 0.5: (0, 3, 0),
        1: (3, 0, 0), 1.5: (0, 0, 3)
    }

    highlight = {
        0: (3, 0, 0), 0.5: (0, 0, 0),
        1: (0, 0, 3), 1.5: (3, 0, 0)
    }

    def do_rainbow(player):
        if player and player.actor and player.actor.node:
            ba.animate_array(player.actor.node,
                             'color', 3, color, True)
            ba.animate_array(player.actor.node,
                             'highlight', 3, highlight, True)
            player.actor.node.handlemessage(
                'celebrate', 6000)

    activity = ba.getactivity()

    if len(args) < 1:
        chatmessage(get_locale('chat_command_not_args_error'))
    elif args[1] == 'all':
        for i in activity.players:
            do_rainbow(i)
    else:
        try:
            do_rainbow(activity.players[int(args[1])])
        except (IndexError, ValueError):
            chatmessage(get_locale('not_player_error'))


# commands handlers for admins
@servercommand('restart'.split(), {Status.ADMIN: 0})
def restart_callback(playerdata: PlayerData, args):
    _ba.quit()


# @servercommand(commands=('/freeze',),
#                                 statuses=(Status.ADMIN,))
# def freeze_callback(playerdata: PlayerData, args):
#     if not args:
#         chatmessage(get_locale('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 i.actor.node.handlemessage(ba.FreezeMessage())
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.sessionplayer.inputdevice._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 i.actor.node.handlemessage(ba.FreezeMessage())
#     else:
#         activity.players[int(args[0])].actor.node.handlemessage(
#             ba.FreezeMessage())
#
#
# @servercommand(commands=('/thaw',),
#                                 statuses=(Status.ADMIN,))
# def thaw_callback(playerdata: PlayerData, args):
#     if not args:
#         chatmessage(get_locale('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 i.actor.node.handlemessage(ba.ThawMessage())
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.sessionplayer.inputdevice._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 i.actor.node.handlemessage(ba.ThawMessage())
#     else:
#         activity.players[int(args[0])].actor.node.handlemessage(
#             ba.ThawMessage())
#
#
# @servercommand(commands=('/kill',),
#                                 statuses=(Status.ADMIN,))
# def kill_callback(playerdata: PlayerData, args):
#     if not args:
#         chatmessage(get_locale('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 i.actor.node.handlemessage(ba.DieMessage())
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.sessionplayer.inputdevice._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 i.actor.node.handlemessage(ba.DieMessage())
#     else:
#         activity.players[int(args[0])].actor.node.handlemessage(
#             ba.DieMessage())
#
#
# @servercommand(commands=('/curse',),
#                                 statuses=(Status.ADMIN,))
# def curse_callback(playerdata: PlayerData, args):
#     if not args:
#         chatmessage(get_locale('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 i.actor.curse()
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.sessionplayer.inputdevice._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 i.actor.curse()
#     else:
#         activity.players[int(args[0])].actor.curse()
#
#
# @servercommand(commands=('/gm',),
#                                 statuses=(Status.ADMIN,))
# def gm_callback(playerdata: PlayerData, args):
#     if not args:
#         chatmessage(get_locale('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 if not i.actor.node.hockey:
#                     i.actor.node.hockey = True
#                 else:
#                     i.actor.node.hockey = False
#
#                 if not i.actor.node.invincible:
#                     i.actor.node.invincible = True
#                 else:
#                     i.actor.node.invincible = False
#
#                 if i.actor._punchPowerScale == 1.2:
#                     i.actor._punchPowerScale = 5
#                 else:
#                     i.actor._punchPowerScale = 1.2
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.sessionplayer.inputdevice._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 if not i.actor.node.hockey:
#                     i.actor.node.hockey = True
#                 else:
#                     i.actor.node.hockey = False
#
#                 if not i.actor.node.invincible:
#                     i.actor.node.invincible = True
#                 else:
#                     i.actor.node.invincible = False
#
#                 if i.actor._punchPowerScale == 1.2:
#                     i.actor._punchPowerScale = 5
#                 else:
#                     i.actor._punchPowerScale = 1.2
#     else:
#         if not activity.players[
#                 int(args[0])].actor.node.hockey:
#             activity.players[
#                 int(args[0])].actor.node.hockey = True
#         else:
#             activity.players[
#                 int(args[0])].actor.node.hockey = False
#
#         if not activity.players[
#                 int(args[0])].actor.node.invincible:
#             activity.players[
#                 int(args[0])].actor.node.invincible = True
#         else:
#             activity.players[
#                 int(args[0])].actor.node.invincible = False
#
#         if not activity.players[
#                 int(args[0])].actor._punchPowerScale == 1.2:
#             activity.players[
#                 int(args[0])].actor._punchPowerScale = 5
#         else:
#             activity.players[
#                 int(args[0])].actor._punchPowerScale = 1.2
#
#
# @servercommand(commands=('/pause',),
#                                 statuses=(Status.ADMIN,))
# def pause_callback(playerdata: PlayerData, args):
#     if not ba.getactivity().globalsnode.paused:
#         ba.getactivity().globalsnode.paused = True
#     else:
#         ba.getactivity().globalsnode.paused = False
#
#
# @servercommand(commands=('/cameraMode', '/cam'),
#                                 statuses=(Status.ADMIN,))
# def camera_mode_callback(playerdata: PlayerData, args):
#     if ba.getactivity().globalsnode.cameraMode == 'follow':
#         ba.getactivity().globalsnode.cameraMode = 'rotate'
#     else:
#         ba.getactivity().globalsnode.cameraMode = 'follow'
#
#
# @servercommand(commands=('/icy',),
#                                 statuses=(Status.ADMIN,))
# def icy_callback(playerdata: PlayerData, args):
#     if not args:
#         chatmessage(get_locale('chat_command_not_args_error')
#     elif len(args) >= 2:
#         activity.players[int(args[0])].actor.node = \
#             activity.players[int(args[1])].actor.node
#
#         activity.players[int(args[1])].actor.node = \
#             activity.players[int(args[0])].actor.node
#
#
# @servercommand(commands=('/maxPlayers', '/mp'),
#                                 statuses=(Status.ADMIN,))
# def max_players_callback(playerdata: PlayerData, args):
#     if not args:
#         chatmessage(get_locale('chat_command_not_args_error')
#     else:
#         activity._maxPlayers = int(args[0])
#         _ba._setPublicPartyMaxSize(int(args[0]))
#
#
# @servercommand(commands=('/rise',),
#                                 statuses=(Status.ADMIN,))
# def rise_callback(playerdata: PlayerData, args):
#     if not args:
#         chatmessage(get_locale('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 activity.spawnPlayer(i)
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.sessionplayer.inputdevice._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 activity.spawnPlayer(i)
#     else:
#         activity.spawnPlayer(activity.players[int(args[0])])
#
#
# @servercommand(commands=('/tnt',),
#                                 statuses=(Status.ADMIN,))
# def tnt_callback(playerdata: PlayerData, args):
#     if not args:
#         chatmessage(get_locale('chat_command_not_args_error')
#     elif args[2] == 'myPos':
#         for i in activity.players:
#             if nick == i.get_name().encode('utf-8'):
#                 pos = i.actor.node.position
#                 ba.Bomb(bombType='tnt',
#                         position=pos).autoRetain()
#     elif len(args) == 3:
#         ba.Bomb(bombType='tnt',
#                 position=(float(args[0]),
#                           float(args[1]),
#                           float(args[2]))).autoRetain()
#
#
# @servercommand(commands=('/bomb',),
#                                 statuses=(Status.ADMIN,))
# def bomb_callback(playerdata: PlayerData, args):
#     if not args:
#         chatmessage(get_locale('chat_command_not_args_error')
#     elif args[0] == 'names':
#         chatmessage(get_locale('bomb_names_text')
#         send_chat_messages(get_locale('arg_bomb_options'))
#         chatmessage(get_locale('dividing_strip_text')
#     elif args[2] == 'myPos':
#         for i in activity.players:
#             if nick == i.get_name().encode('utf-8'):
#                 pos = i.actor.node.position
#                 ba.Bomb(bombType=str(args[0]),
#                         blastRadius=float(args[1]),
#                         position=pos).autoRetain()
#     elif len(args) == 5:
#         ba.Bomb(bombType=str(args[0]),
#                 blastRadius=float(args[1]),
#                 position=(float(args[2]),
#                           float(args[3]),
#                           float(args[4]))).autoRetain()
#
#
# @servercommand(commands=('/blast',),
#                                 statuses=(Status.ADMIN,))
# def blast_callback(playerdata: PlayerData, args):
#     if not args:
#         chatmessage(get_locale('chat_command_not_args_error')
#     elif args[1] == 'myPos':
#         for i in activity.players:
#             if nick == i.get_name().encode('utf-8'):
#                 pos = i.actor.node.position
#                 ba.Blast(blastRadius=float(args[0]),
#                          position=pos).autoRetain()
#     elif len(args) == 4:
#         ba.Blast(blastRadius=float(args[0]),
#                  position=(float(args[1]),
#                            float(args[2]),
#                            float(args[3]))).autoRetain()
#
#
# @servercommand(commands=('/powerup', '/bonus'),
#                                 statuses=(Status.ADMIN,))
# def powerup_callback(playerdata: PlayerData, args):
#     if not args:
#         chatmessage(get_locale('chat_command_not_args_error')
#     elif args[0] == 'names':
#         chatmessage(get_locale('powerup_names_text')
#         send_chat_messages(get_locale('arg_powerup_options'))
#         chatmessage(get_locale('dividing_strip_text')
#     elif args[1] == 'myPos':
#         for i in activity.players:
#             if nick == i.get_name().encode('utf-8'):
#                 pos = i.actor.node.position
#                 ba.Powerup(powerupType=str(args[0]),
#                            position=pos).autoRetain()
#     elif len(args) == 4:
#         ba.Powerup(powerupType=str(args[0]),
#                    position=(float(args[1]),
#                              float(args[2]),
#                              float(args[3]))).autoRetain()
#
#
# @servercommand(commands=('/inv',),
#                                 statuses=(Status.ADMIN,))
# def inv_callback(playerdata: PlayerData, args):
#     if not args:
#         chatmessage(get_locale('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 i.actor.node.name = ''
#                 i.actor.node.colorTexture = None
#                 i.actor.node.colorMaskTexture = None
#                 i.actor.node.headModel = None
#                 i.actor.node.torsoModel = None
#                 i.actor.node.pelvisModel = None
#                 i.actor.node.upperArmModel = None
#                 i.actor.node.foreArmModel = None
#                 i.actor.node.handModel = None
#                 i.actor.node.upperLegModel = None
#                 i.actor.node.lowerLegModel = None
#                 i.actor.node.toesModel = None
#                 i.actor.node.style = 'cyborg'
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.sessionplayer.inputdevice._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 i.actor.node.name = ''
#                 i.actor.node.colorTexture = None
#                 i.actor.node.colorMaskTexture = None
#                 i.actor.node.headModel = None
#                 i.actor.node.torsoModel = None
#                 i.actor.node.pelvisModel = None
#                 i.actor.node.upperArmModel = None
#                 i.actor.node.foreArmModel = None
#                 i.actor.node.handModel = None
#                 i.actor.node.upperLegModel = None
#                 i.actor.node.lowerLegModel = None
#                 i.actor.node.toesModel = None
#                 i.actor.node.style = 'cyborg'
#     else:
#         t = activity.players[int(args[0])].actor.node
#         t.name = ''
#         t.colorTexture = None
#         t.colorMaskTexture = None
#         t.headModel = None
#         t.torsoModel = None
#         t.pelvisModel = None
#         t.upperArmModel = None
#         t.foreArmModel = None
#         t.handModel = None
#         t.upperLegModel = None
#         t.lowerLegModel = None
#         t.toesModel = None
#         t.style = 'cyborg'
#
#
# @servercommand(commands=('/ban',),
#                                 statuses=(Status.ADMIN,))
# def ban_callback(playerdata: PlayerData, args):
#     if len(args) < 2 or (args[0] == 'device' and len(args) < 3):
#         chatmessage(get_locale('chat_command_not_args_error')
#     elif args[0] == 'device':
#         for p in activity.players:
#             operator = None
#             account_id = None
#
#             bd_server_player = bd.server.get_player('client_id',
#                                                     client_id)
#             if 'id' in bd_server_player:
#                 operator = bd_server_player['id']
#
#             account_name = p.sessionplayer.inputdevice._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 account_id = p.get_account_id()
#
#             try:
#                 end = args[3]
#             except IndexError:
#                 end = None
#
#             _ba._disconnectClient(p.sessionplayer.inputdevice.client_id())
#             if account_id is not None:
#                 api.player.ban.add(
#                     in_thread=True,
#                     id=account_id,
#                     reason=args[2],
#                     operator=operator,
#                     end=end)
#     else:
#         operator = "CONSOLE"
#         account_id = None
#
#         bd_server_player = bd.server.get_player('client_id',
#                                                 client_id)
#         if 'id' in bd_server_player:
#             operator = bd_server_player['id']
#
#         account_id = activity.players[int(args[0])].get_account_id()
#
#         try:
#             end = args[2]
#         except IndexError:
#             end = None
#
#         _ba._disconnectClient(activity.players[int(args[0])].sessionplayer.inputdevice.client_id())
#         if account_id is not None:
#             api.player.ban.add(
#                 in_thread=True,
#                 id=account_id,
#                 reason=args[1],
#                 operator=operator,
#                 end=end)
#
#
# @servercommand(commands=['/fakekickvote', '/fkv'],
#                                 statuses=[Status.ADMIN])
# def fakekickvote_callback(playerdata: PlayerData, args):
#     if not args:
#         chatmessage(get_locale('chat_command_not_args_error')
#     else:
#         activity = _ba._getForegroundHostActivity()
#
#         p = activity.players[int(args[0])]
#         device = p.sessionplayer.inputdevice
#         ba.screenMessage(get_format_locale('kickvote_start', name=p.get_name()), color=(1, 1, 0))
#         ba.screenMessage(get_format_locale('kickvote_type'), color=(1, 1, 0))
#         ba.screenMessage(get_format_locale('kickvote_needed_num', n='4'), color=(1, 1, 0))
#
# @servercommand(func=lambda m: check_message_for_team(m),
#                                 statuses=['anyone'])
# def team_detect_callback(playerdata: PlayerData, args):
#     activity = _ba._getForegroundHostActivity()
#
#     device = None
#     player = None
#     for p in activity.players:
#         if client_id == p.sessionplayer.inputdevice.client_id():
#             device = p.sessionplayer.inputdevice
#             player = p
#             break
#
#     chatmessage(get_locale('team_warn', name=device.player.sessionplayer.get_name(),
#                         account_id=player.get_account_id())
