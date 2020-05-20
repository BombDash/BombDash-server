# -*- coding: utf-8 -*-
import random
import weakref

import ba
import _ba

from bd.me import redefine_flag, redefine_class_methods, RedefineFlag


def get_locale(*args):
    return 'Error'


@redefine_class_methods(ba.Chooser)
class Chooser:
    _redefine_methods = ('__init__', '_get_glowing_colors', 'update_from_player_profiles',
                         '_get_name')

    @redefine_flag(RedefineFlag.DECORATE_ADVANCED)
    def __init__(self, vpos, player, lobby, old_function):
        self.glow_dict = {}
        self._markers = ('"', "'", '^', '%', ';', '`')
        old_function(self, vpos, player, lobby)
        self._get_glowing_colors()
        self.update_from_player_profiles()

    @redefine_flag(RedefineFlag.REDEFINE)
    def _get_glowing_colors(self):
        """Search glowing code among profiles."""
        try:
            should_del = []
            for i in self._profilenames:
                for m in self._markers:
                    if i.startswith(m + ','):
                        code = i.split(',')
                        self.glow_dict[code[0]] = (
                            float(code[1]),
                            float(code[2]),
                            int(code[3]),
                            int(code[4]))
                        should_del.append(i)
            for i in should_del:
                self._profilenames.remove(i)
        except Exception as err:
            print(err)
            ba.screenmessage(
                get_locale('init_glowing_code_error'),
                color=(1, 0, 0),
                clients=[self._player.get_input_device().client_id],
                transient=True)

    @redefine_flag(RedefineFlag.DECORATE_ADVANCED)
    def _get_name(self, full=True, old_function=None):
        name = old_function(self, full)
        for m in self._markers:
            name = name.replace(m, '')
        return name

    @redefine_flag(RedefineFlag.DECORATE_ADVANCED)
    def update_from_player_profiles(self, old_function):
        from ba import _profile
        try:
            self._profilename = self._profilenames[self._profileindex]
            character = self.profiles[self._profilename]['character']

            if self._profilename[0] in self.glow_dict:
                if (character not in self.character_names
                        and character in _ba.app.spaz_appearances):
                    self.character_names.append(character)
                self.character_index = self.character_names.index(character)

                player_glowing_dict = self.glow_dict[self._profilename[0]]
                color_marker = player_glowing_dict[0]
                color_marker = max(-25.0, min(color_marker, 25.0))

                highlight_marker = float(player_glowing_dict[1])
                highlight_marker = max(-25.0, min(highlight_marker, 25.0))

                stabilize_color = int(player_glowing_dict[2]) > 0
                stabilize_highlight = int(player_glowing_dict[3]) > 0
                self._color, self._highlight = \
                    _profile.get_player_profile_colors(
                        self._profilename,
                        profiles=self.profiles)

                if stabilize_color:
                    m = max(self._color)
                    self._color = list(self._color)
                    for i in (0, 1, 2):
                        if self._color[i] == m:
                            self._color[i] = self._color[i] * color_marker
                    self._color = tuple(self._color)
                else:
                    self._color = (
                        self._color[0] * color_marker,
                        self._color[1] * color_marker,
                        self._color[2] * color_marker)

                if not stabilize_highlight:
                    self._highlight = (
                        self._highlight[0] * highlight_marker,
                        self._highlight[1] * highlight_marker,
                        self._highlight[2] * highlight_marker)
                else:
                    m = max(self._highlight)
                    self._highlight = list(self._highlight)
                    for i in (0, 1, 2):
                        if self._highlight[i] == m:
                            self._highlight[i] = \
                                self._highlight[i] * highlight_marker
                    self._highlight = tuple(self._highlight)
            else:
                old_function(self)
        except Exception:
            self.character_index = self._random_character_index
            self._color = self._random_color
            self._highlight = self._random_highlight

        self._update_icon()
        self._update_text()
