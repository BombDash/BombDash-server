from bd.httpapi import sharedapi as serverapi
from bd.me import redefine_flag, redefine_class_methods, RedefineFlag
from bd.playerdata import PlayerData, PrefixData, ParticleData, add_player, del_player, Status

import ba


@redefine_class_methods(ba.GameActivity)
class GameActivity(ba.Activity):
    _redefine_methods = 'on_player_join'.split()

    @redefine_flag(RedefineFlag.DECORATE_PRE)
    def on_player_join(self, player: ba.Player) -> None:
        account_id = player.sessionplayer.get_account_id()
        info = serverapi.player.get(id=account_id)
        p_data = PlayerData(
            id=account_id,
            client_id=player.sessionplayer.inputdevice.client_id,
            status=Status(info['status']) if 'status' in info else 'player',
            prefix=PrefixData(
                **info['prefix']
            ) if 'prefix' in info and info['prefix'] else None,
            particle=ParticleData(
                **info['particle']
            ) if 'particle' in info and info['particle'] else None
        )
        add_player(p_data)
