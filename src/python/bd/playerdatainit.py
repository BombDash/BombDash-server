from bd.me import redefine_flag, redefine_class_methods, RedefineFlag
from bd.playerdata import PlayerData, PrefixData, ParticleData, add_player, del_player, Status

import ba


@redefine_class_methods(ba.GameActivity)
class GameActivity(ba.Activity):
    _redefine_methods = 'on_player_join'.split()

    @redefine_flag(RedefineFlag.DECORATE_PRE)
    def on_player_join(self, player: ba.Player) -> None:
        p_data = PlayerData(
            id=player.sessionplayer.get_account_id(),
            status=Status.ADMIN.value,  # TODO: админ ну да ну да
            prefix=PrefixData(
                text='super prefix',
                speed=250,
                animation=(-65528, -16713473, -15335680)
            ),
            particle=ParticleData(
                particle_type='1',
                emit_type='ice'
            )
        )
        add_player(p_data)
