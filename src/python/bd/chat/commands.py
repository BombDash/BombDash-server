import ba
from _ba import chatmessage
import _ba

from bd.chat.commands_engine import servercommand, _handlers
from bd.playerdata import PlayerData, Status
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
            _ba.disconnect_client(int(args[1]),
                                  ban_time=ban_time)
        else:
            chatmessage(get_locale('not_player_error'))


@servercommand('remove'.split(), {Status.ADMIN: 0, Status.VIP: 60})
def remove_handler(playerdata: PlayerData, args):
    raise Exception()
    activity = _ba.get_foreground_host_activity()
    if len(args) < 2:
        chatmessage(get_locale('chat_command_not_args_error'))
    elif args[0] == 'all':
        for player in activity.players:
            player.sessionplayer.remove_from_game()
    else:
        activity.players[int(args[0])].sessionplayer.remove_from_game()


# @bd.server.chat.message_handler(commands=('/end',),
#                                 statuses=('vip', 'admin'))
# def end_handler(activity, args, status, client_id):
#     activity.end_game()
#
#
# @bd.server.chat.message_handler(commands=('/ooh', '/o'),
#                                 statuses=('vip', 'admin'))
# def ooh_handler(activity, args, status, client_id):
#     ba.playsound(ba.getsound('ooh'), volume=2)
#
#
# @bd.server.chat.message_handler(commands=('/playSound', '/ps'),
#                                 statuses=('vip', 'admin'))
# def play_sound_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     else:
#         ba.playsound(ba.getsound(str(args[0])), volume=2)
#
#
# @bd.server.chat.message_handler(commands=('/nv',),
#                                 statuses=('vip', 'admin'))
# def nv_handler(activity, args, status, client_id):
#     tint = {0: ba.sharedobj('globals').tint,
#             1000: (0.5, 0.7, 1.0)}
#
#     ba.animateArray(ba.sharedobj('globals'), 'tint', 3, tint)
#
#
# @bd.server.chat.message_handler(commands=('/dv',),
#                                 statuses=('vip', 'admin'))
# def dv_handler(activity, args, status, client_id):
#     tint = {0: ba.sharedobj('globals').tint,
#             1000: (1.0, 1.0, 1.0)}
#
#     ba.animateArray(ba.sharedobj('globals'), 'tint', 3, tint)
#
#
# @bd.server.chat.message_handler(commands=('/box',),
#                                 statuses=('vip', 'admin'))
# def box_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 i.actor.node.torsoModel = ba.getmodel('tnt')
#                 i.actor.node.colorMaskTexture = ba.gettexture('tnt')
#                 i.actor.node.colorTexture = ba.gettexture('tnt')
#                 i.actor.node.highlight = (1, 1, 1)
#                 i.actor.node.color = (1, 1, 1)
#                 i.actor.node.headModel = None
#                 i.actor.node.style = 'cyborg'
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.getInputDevice()._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 i.actor.node.torsoModel = ba.getmodel('tnt')
#                 i.actor.node.colorMaskTexture = ba.gettexture('tnt')
#                 i.actor.node.colorTexture = ba.gettexture('tnt')
#                 i.actor.node.highlight = (1, 1, 1)
#                 i.actor.node.color = (1, 1, 1)
#                 i.actor.node.headModel = None
#                 i.actor.node.style = 'cyborg'
#     else:
#         activity.players[int(args[0])].actor.node.torsoModel = \
#             ba.getmodel('tnt')
#
#         activity.players[
#             int(args[0])].actor.node.colorMaskTexture = \
#             ba.gettexture('tnt')
#
#         activity.players[int(args[0])].actor.node.colorTexture = \
#             ba.gettexture('tnt')
#
#         activity.players[int(args[0])].actor.node.highlight = \
#             (1, 1, 1)
#
#         activity.players[int(args[0])].actor.node.color = \
#             (1, 1, 1)
#
#         activity.players[int(args[0])].actor.node.headModel = \
#             None
#
#         activity.players[int(args[0])].actor.node.style = \
#             'cyborg'
#
#
# @bd.server.chat.message_handler(commands=('/hug',),
#                                 statuses=('vip', 'admin'))
# def hug_handler(activity, args, status, client_id):
#     if not args:
#         try:
#             activity.players[0].actor.node.holdNode = \
#                 activity.players[1].actor.node
#         except Exception:
#             pass
#
#         try:
#             activity.players[1].actor.node.holdNode = \
#                 activity.players[0].actor.node
#         except Exception:
#             pass
#
#         try:
#             activity.players[2].actor.node.holdNode = \
#                 activity.players[3].actor.node
#         except Exception:
#             pass
#
#         try:
#             activity.players[3].actor.node.holdNode = \
#                 activity.players[2].actor.node
#         except Exception:
#             pass
#
#         try:
#             activity.players[4].actor.node.holdNode = \
#                 activity.players[5].actor.node
#         except Exception:
#             pass
#
#         try:
#             activity.players[5].actor.node.holdNode = \
#                 activity.players[4].actor.node
#         except Exception:
#             pass
#
#         try:
#             activity.players[6].actor.node.holdNode = \
#                 activity.players[7].actor.node
#         except Exception:
#             pass
#
#         try:
#             activity.players[7].actor.node.holdNode = \
#                 activity.players[6].actor.node
#         except Exception:
#             pass
#     else:
#         activity.players[int(args[0])].actor.node.holdNode = \
#             activity.players[int(args[1])].actor.node
#
#
# @bd.server.chat.message_handler(commands=('/tint',),
#                                 statuses=('vip', 'admin'))
# def tint_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'r':
#         m = 1.3 if args[1] is None else float(args[1])
#         s = 1000 if args[2] is None else float(args[2])
#         tint = {
#             0: (1 * m, 0, 0), s: (0, 1 * m, 0),
#             s * 2: (0, 0, 1 * m), s * 3: (1 * m, 0, 0)
#         }
#
#         ba.animateArray(ba.sharedobj('globals'),
#                         'tint', 3, tint, True)
#     else:
#         ba.sharedobj('globals').tint = (float(args[0]),
#                                         float(args[1]),
#                                         float(args[2]))
#
#
# @bd.server.chat.message_handler(commands=('/sm',),
#                                 statuses=('vip', 'admin'))
# def sm_handler(activity, args, status, client_id):
#     if not ba.sharedobj('globals').slowMotion:
#         ba.sharedobj('globals').slowMotion = True
#     else:
#         ba.sharedobj('globals').slowMotion = False
#
#
# @bd.server.chat.message_handler(commands=('/gp',),
#                                 statuses=('vip', 'admin'))
# def gp_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     else:
#         send_locale_message('player_profiles_text')
#         profiles = activity.players[int(args[0])].getInputDevice(
#         )._getPlayerProfiles()
#
#         for i in profiles:
#             try:
#                 if i.encode('utf-8') == '__account__':
#                     input_device = activity.players[
#                         int(args[0])].getInputDevice()
#
#                     i = input_device._getAccountName(False)
#
#                 baInternal._chatMessage(i)
#             except Exception:
#                 pass
#
#         send_locale_message('dividing_strip_text')
#
#
# @bd.server.chat.message_handler(commands=('/fly',),
#                                 statuses=('vip', 'admin'))
# def fly_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 i.actor.node.fly = True
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.getInputDevice()._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 i.actor.node.fly = True
#     else:
#         if not activity.players[int(args[0])].actor.node.fly:
#             activity.players[int(args[0])].actor.node.fly = True
#         else:
#             activity.players[int(args[0])].actor.node.fly = False
#
#
# @bd.server.chat.message_handler(commands=('/ac',),
#                                 statuses=('vip', 'admin'))
# def ac_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'r':
#         m = 1.3 if args[1] is None else float(args[1])
#         s = 1000 if args[2] is None else float(args[2])
#         ambient_color = {
#             0: (1 * m, 0, 0), s: (0, 1 * m, 0),
#             s * 2: (0, 0, 1 * m), s * 3: (1 * m, 0, 0)
#         }
#
#         ba.animateArray(ba.sharedobj('globals'),
#                         'ambientColor', 3, ambient_color, True)
#     else:
#         ba.sharedobj('globals').ambientColor = (float(args[0]),
#                                                 float(args[1]),
#                                                 float(args[2]))
#
#
# @bd.server.chat.message_handler(commands=('/iceOff', '/io'),
#                                 statuses=('vip', 'admin'))
# def ice_off_handler(activity, args, status, client_id):
#     activity.map.node.materials = [
#         ba.sharedobj('footingMaterial')]
#
#     activity.map.floor.materials = [
#         ba.sharedobj('footingMaterial')]
#
#     activity.map.isHockey = False
#     for i in activity.players:
#         try:
#             i.actor.node.hockey = False
#         except Exception:
#             pass
#
#
# @bd.server.chat.message_handler(commands=('/heal',),
#                                 statuses=('vip', 'admin'))
# def heal_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 i.actor.node.handlemessage(
#                     ba.PowerupMessage(powerupType='health'))
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.getInputDevice()._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 i.actor.node.handlemessage(
#                     ba.PowerupMessage(powerupType='health'))
#     else:
#         activity.players[int(args[0])].actor.node.handlemessage(
#             ba.PowerupMessage(powerupType='health'))
#
#
# @bd.server.chat.message_handler(commands=('/reflections', '/ref'),
#                                 statuses=('vip', 'admin'))
# def reflections_handler(activity, args, status, client_id):
#     rs = [int(args[1])]
#     ref_type = 'soft' if int(args[0]) == 0 else 'powerup'
#
#     try:
#         activity.map.node.reflection = ref_type
#         activity.map.node.reflectionScale = rs
#     except Exception:
#         pass
#
#     try:
#         activity.map.bg.reflection = ref_type
#         activity.map.bg.reflectionScale = rs
#     except Exception:
#         pass
#
#     try:
#         activity.map.floor.reflection = ref_type
#         activity.map.floor.reflectionScale = rs
#     except Exception:
#         pass
#
#     try:
#         activity.map.center.reflection = ref_type
#         activity.map.center.reflectionScale = rs
#     except Exception:
#         pass
#
#
# @bd.server.chat.message_handler(commands=('/shatter',),
#                                 statuses=('vip', 'admin'))
# def shatter_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 i.actor.node.shattered = int(args[1])
#             except Exception:
#                 pass
#     else:
#         activity.players[
#             int(args[0])].actor.node.shattered = int(args[1])
#
#
# @bd.server.chat.message_handler(commands=('/cm',),
#                                 statuses=('vip', 'admin'))
# def cm_handler(activity, args, status, client_id):
#     if not args:
#         time = 10000
#     else:
#         time = int(args[0])
#
#     op = 0.08
#     std = ba.sharedobj('globals').vignetteOuter
#     vignetteOuter = {
#         0: ba.sharedobj('globals').vignetteOuter,
#         17000: (0, 1, 0)
#     }
#
#     ba.animateArray(ba.sharedobj('globals'),
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
#             0: ba.sharedobj('globals').vignetteOuter,
#             100: std
#         }
#
#         ba.animateArray(ba.sharedobj('globals'),
#                         'vignetteOuter', 3, vignetteOuter)
#
#     ba.timer(time, off)
#
#
# @bd.server.chat.message_handler(commands=('/sleep',),
#                                 statuses=('vip', 'admin'))
# def sleep_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 i.actor.node.handlemessage('knockout', 5000)
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.getInputDevice()._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 i.actor.node.handlemessage('knockout', 5000)
#     else:
#         activity.players[int(args[0])].actor.node.handlemessage(
#             'knockout', 5000)
#
#
# @bd.server.chat.message_handler(commands=('/skin',),
#                                 statuses=('vip', 'admin'))
# def skin_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'names':
#         send_locale_message('skin_names_text')
#         send_chat_messages(get_locale('skin_names'))
#         send_locale_message('dividing_strip_text')
#     elif str(args[1]) in SKIN_NAMES:
#         account_id = activity.players[int(args[0])].get_account_id()
#         bd.server.custom_skins[account_id] = str(args[1])
#     elif str(args[1]) == 'reset':
#         account_id = activity.players[int(args[0])].get_account_id()
#         bd.server.custom_skins.pop(account_id, None)
#
#
# @bd.server.chat.message_handler(commands=('/rainbow',),
#                                 statuses=('vip', 'admin'))
# def rainbow_handler(activity, args, status, client_id):
#     color = {
#         0: (0, 0, 3), 500: (0, 3, 0),
#         1000: (3, 0, 0), 1500: (0, 0, 3)
#     }
#
#     highlight = {
#         0: (3, 0, 0), 500: (0, 0, 0),
#         1000: (0, 0, 3), 1500: (3, 0, 0)
#     }
#
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 ba.animateArray(i.actor.node, 'color', 3,
#                                 color, True)
#
#                 ba.animateArray(i.actor.node, 'highlight', 3,
#                                 highlight, True)
#
#                 i.actor.node.handlemessage('celebrate', 100000000)
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.getInputDevice()._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 ba.animateArray(i.actor.node, 'color', 3,
#                                 color, True)
#
#                 ba.animateArray(i.actor.node, 'highlight', 3,
#                                 highlight, True)
#
#                 i.actor.node.handlemessage('celebrate', 100000000)
#     else:
#         ba.animateArray(activity.players[int(args[0])].actor.node,
#                         'color', 3, color, True)
#
#         ba.animateArray(activity.players[int(args[0])].actor.node,
#                         'highlight', 3, highlight, True)
#
#         activity.players[int(args[0])].actor.node.handlemessage(
#             'celebrate', 100000000)
#
#
# # commands handlers for admins
# @bd.server.chat.message_handler(commands=('/restart',),
#                                 statuses=('admin',))
# def restart_handler(activity, args, status, client_id):
#     baInternal.quit()
#
#
# @bd.server.chat.message_handler(commands=('/freeze',),
#                                 statuses=('admin',))
# def freeze_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 i.actor.node.handlemessage(ba.FreezeMessage())
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.getInputDevice()._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 i.actor.node.handlemessage(ba.FreezeMessage())
#     else:
#         activity.players[int(args[0])].actor.node.handlemessage(
#             ba.FreezeMessage())
#
#
# @bd.server.chat.message_handler(commands=('/thaw',),
#                                 statuses=('admin',))
# def thaw_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 i.actor.node.handlemessage(ba.ThawMessage())
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.getInputDevice()._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 i.actor.node.handlemessage(ba.ThawMessage())
#     else:
#         activity.players[int(args[0])].actor.node.handlemessage(
#             ba.ThawMessage())
#
#
# @bd.server.chat.message_handler(commands=('/kill',),
#                                 statuses=('admin',))
# def kill_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 i.actor.node.handlemessage(ba.DieMessage())
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.getInputDevice()._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 i.actor.node.handlemessage(ba.DieMessage())
#     else:
#         activity.players[int(args[0])].actor.node.handlemessage(
#             ba.DieMessage())
#
#
# @bd.server.chat.message_handler(commands=('/curse',),
#                                 statuses=('admin',))
# def curse_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 i.actor.curse()
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.getInputDevice()._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 i.actor.curse()
#     else:
#         activity.players[int(args[0])].actor.curse()
#
#
# @bd.server.chat.message_handler(commands=('/gm',),
#                                 statuses=('admin',))
# def gm_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
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
#             account_name = i.getInputDevice()._getAccountName(
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
#             int(args[0])].actor.node.hockey:
#             activity.players[
#                 int(args[0])].actor.node.hockey = True
#         else:
#             activity.players[
#                 int(args[0])].actor.node.hockey = False
#
#         if not activity.players[
#             int(args[0])].actor.node.invincible:
#             activity.players[
#                 int(args[0])].actor.node.invincible = True
#         else:
#             activity.players[
#                 int(args[0])].actor.node.invincible = False
#
#         if not activity.players[
#                    int(args[0])].actor._punchPowerScale == 1.2:
#             activity.players[
#                 int(args[0])].actor._punchPowerScale = 5
#         else:
#             activity.players[
#                 int(args[0])].actor._punchPowerScale = 1.2
#
#
# @bd.server.chat.message_handler(commands=('/pause',),
#                                 statuses=('admin',))
# def pause_handler(activity, args, status, client_id):
#     if not ba.sharedobj('globals').paused:
#         ba.sharedobj('globals').paused = True
#     else:
#         ba.sharedobj('globals').paused = False
#
#
# @bd.server.chat.message_handler(commands=('/cameraMode', '/cam'),
#                                 statuses=('admin',))
# def camera_mode_handler(activity, args, status, client_id):
#     if ba.sharedobj('globals').cameraMode == 'follow':
#         ba.sharedobj('globals').cameraMode = 'rotate'
#     else:
#         ba.sharedobj('globals').cameraMode = 'follow'
#
#
# @bd.server.chat.message_handler(commands=('/icy',),
#                                 statuses=('admin',))
# def icy_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif len(args) >= 2:
#         activity.players[int(args[0])].actor.node = \
#             activity.players[int(args[1])].actor.node
#
#         activity.players[int(args[1])].actor.node = \
#             activity.players[int(args[0])].actor.node
#
#
# @bd.server.chat.message_handler(commands=('/maxPlayers', '/mp'),
#                                 statuses=('admin',))
# def max_players_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     else:
#         activity._maxPlayers = int(args[0])
#         baInternal._setPublicPartyMaxSize(int(args[0]))
#
#
# @bd.server.chat.message_handler(commands=('/rise',),
#                                 statuses=('admin',))
# def rise_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'all':
#         for i in activity.players:
#             try:
#                 activity.spawnPlayer(i)
#             except Exception:
#                 pass
#     elif args[0] == 'device':
#         for i in activity.players:
#             account_name = i.getInputDevice()._getAccountName(
#                 False).encode('utf-8')
#
#             if account_name == args[1]:
#                 activity.spawnPlayer(i)
#     else:
#         activity.spawnPlayer(activity.players[int(args[0])])
#
#
# @bd.server.chat.message_handler(commands=('/tnt',),
#                                 statuses=('admin',))
# def tnt_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
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
# @bd.server.chat.message_handler(commands=('/bomb',),
#                                 statuses=('admin',))
# def bomb_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'names':
#         send_locale_message('bomb_names_text')
#         send_chat_messages(get_locale('arg_bomb_options'))
#         send_locale_message('dividing_strip_text')
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
# @bd.server.chat.message_handler(commands=('/blast',),
#                                 statuses=('admin',))
# def blast_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
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
# @bd.server.chat.message_handler(commands=('/powerup', '/bonus'),
#                                 statuses=('admin',))
# def powerup_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     elif args[0] == 'names':
#         send_locale_message('powerup_names_text')
#         send_chat_messages(get_locale('arg_powerup_options'))
#         send_locale_message('dividing_strip_text')
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
# @bd.server.chat.message_handler(commands=('/inv',),
#                                 statuses=('admin',))
# def inv_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
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
#             account_name = i.getInputDevice()._getAccountName(
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
# @bd.server.chat.message_handler(commands=('/ban',),
#                                 statuses=('admin',))
# def ban_handler(activity, args, status, client_id):
#     if len(args) < 2 or (args[0] == 'device' and len(args) < 3):
#         send_locale_message('chat_command_not_args_error')
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
#             account_name = p.getInputDevice()._getAccountName(
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
#             baInternal._disconnectClient(p.getInputDevice().getClientID())
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
#         baInternal._disconnectClient(activity.players[int(args[0])].getInputDevice().getClientID())
#         if account_id is not None:
#             api.player.ban.add(
#                 in_thread=True,
#                 id=account_id,
#                 reason=args[1],
#                 operator=operator,
#                 end=end)
#
#
# @bd.server.chat.message_handler(commands=['/fakekickvote', '/fkv'],
#                                 statuses=['admin'])
# def fakekickvote_handler(activity, args, status, client_id):
#     if not args:
#         send_locale_message('chat_command_not_args_error')
#     else:
#         activity = baInternal._getForegroundHostActivity()
#
#         p = activity.players[int(args[0])]
#         device = p.getInputDevice()
#         ba.screenMessage(get_format_locale('kickvote_start', name=p.get_name()), color=(1, 1, 0))
#         ba.screenMessage(get_format_locale('kickvote_type'), color=(1, 1, 0))
#         ba.screenMessage(get_format_locale('kickvote_needed_num', n='4'), color=(1, 1, 0))
#
#
# @bd.server.chat.message_handler(func=lambda m: check_message_for_team(m),
#                                 statuses=['anyone'])
# def team_detect_handler(activity, args, status, client_id):
#     activity = baInternal._getForegroundHostActivity()
#
#     device = None
#     player = None
#     for p in activity.players:
#         if client_id == p.getInputDevice().getClientID():
#             device = p.getInputDevice()
#             player = p
#             break
#
#     send_locale_message('team_warn', name=device.player.sessionplayer.get_name(),
#                         account_id=player.get_account_id())
