import random

import ba
from bastd.actor import spaz as stdspaz

from bd.me import redefine_flag, redefine_class_methods, RedefineFlag


def get_locale(key):
    locales = {
        "fatality_text": "FATALITY!!!",
        "crazy_text": "CRAZY!!",
        "aggressive_text": "AGGRESSIVE!"
    }
    return locales.get(key)


@redefine_class_methods(stdspaz.Spaz)
class Spaz(ba.Actor):
    _redefine_methods = ('handlemessage',)

    @redefine_flag(RedefineFlag.DECORATE_AFTER)
    def handlemessage(self, msg, returned):
        from bastd.actor.popuptext import PopupText
        if isinstance(msg, ba.HitMessage):
            if msg.hit_type == 'punch':
                if not self.node:
                    return None
                if self.node.invincible:
                    return True
                mag = msg.magnitude * self.impact_scale
                velocity_mag = msg.velocity_magnitude * self.impact_scale
                damage_scale = 0.22

                # If they've got a shield, deliver it to that instead.
                if self.shield:
                    if msg.flat_damage:
                        damage = msg.flat_damage * self.impact_scale
                    else:
                        damage = damage_scale * self.node.damage

                    # Its a cleaner event if a hit just kills the shield
                    # without damaging the player.
                    # However, massive damage events should still be able to
                    # damage the player. This hopefully gives us a happy medium.
                    max_spillover = stdspaz.get_factory().max_shield_spillover_damage

                    # If they passed our spillover threshold,
                    # pass damage along to spaz.
                    if self.shield_hitpoints <= -max_spillover:
                        leftover_damage = -max_spillover - self.shield_hitpoints
                        shield_leftover_ratio = leftover_damage / damage

                        # Scale down the magnitudes applied to spaz accordingly.
                        mag *= shield_leftover_ratio
                        velocity_mag *= shield_leftover_ratio
                    else:
                        return True  # Good job shield!
                else:
                    shield_leftover_ratio = 1.0

                if msg.flat_damage:
                    damage = int(msg.flat_damage * self.impact_scale *
                                 shield_leftover_ratio)
                else:
                    damage = int(damage_scale * self.node.damage)

                if damage > 999:
                    PopupText(
                        get_locale('fatality_text'),
                        color=(0.905, 0.298, 0.235),
                        scale=2.0,
                        position=self.node.position).autoretain()

                    ba.emitfx(
                        position=msg.pos,
                        chunk_type='spark',
                        velocity=(msg.force_direction[0] * 1.3,
                                  msg.force_direction[1] * 1.3 + 5.0,
                                  msg.force_direction[2] * 1.3),
                        count=45,
                        scale=1.0,
                        spread=1.0)

                    self.lightning_bolt(
                        position=self.node.position,
                        radius=3)
                elif 800 < damage < 999:
                    PopupText(
                        get_locale('crazy_text'),
                        color=(0.180, 0.800, 0.443),
                        scale=1.5,
                        position=self.node.position).autoretain()

                    ba.emitfx(
                        position=msg.pos,
                        chunk_type='spark',
                        velocity=(msg.force_direction[0] * 1.3,
                                  msg.force_direction[1] * 1.3 + 5.0,
                                  msg.force_direction[2] * 1.3),
                        count=45,
                        scale=1.0,
                        spread=1.0)
                elif 750 < damage < 800:
                    PopupText(
                        get_locale('aggressive_text'),
                        color=(0.231, 0.596, 0.858),
                        scale=1.5,
                        position=self.node.position).autoretain()
        return returned
