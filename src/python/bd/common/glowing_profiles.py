import ba
import _ba

from bd.me import redefine_flag, redefine_class_methods, RedefineFlag
from bd.locale import get_locale


@redefine_class_methods(ba.Chooser)
class Chooser:
    _redefine_methods = ('_gcinit', '_get_glowing_colors', 'update_from_profile',
                         '_getname')

    def _gcinit(self):
        if hasattr(self, '_gcinit_done'):
            return
        self.glow_dict = {}
        self._markers = ('"', "'", '^', '%', ';', '`')
        self._get_glowing_colors()
        self._gcinit_done = True

    @redefine_flag(RedefineFlag.REDEFINE)
    def _get_glowing_colors(self):
        """Search glowing code among profiles."""
        should_del = []
        for i in self._profilenames:
            for m in self._markers:
                if i.startswith(m + ','):
                    try:
                        code = i.split(',')
                        self.glow_dict[code[0]] = (
                            float(code[1]),
                            float(code[2]),
                            int(code[3]),
                            int(code[4]))
                        # should_del.append(i)
                    except Exception as err:
                        print(err)
                        ba.screenmessage(
                            f"{i}: {get_locale('init_glowing_code_error')}",
                            color=(1, 0, 0),
                            clients=[self._sessionplayer.inputdevice.client_id],
                            transient=True)
        for i in should_del:
            self._profilenames.remove(i)

    @redefine_flag(RedefineFlag.DECORATE_ADVANCED)
    def _getname(self, full=True, old_function=None):
        name = old_function(self, full)
        for m in self._markers:
            name = name.replace(m, '')
        return name

    @redefine_flag(RedefineFlag.DECORATE_ADVANCED)
    def update_from_profile(self, old_function):
        self._gcinit()
        from ba import _profile
        try:
            self._profilename = self._profilenames[self._profileindex]
            character = self._profiles[self._profilename]['character']

            if self._profilename[0] in self.glow_dict:
                if (character not in self._character_names
                        and character in _ba.app.spaz_appearances):
                    self._character_names.append(character)
                self._character_index = self._character_names.index(character)

                player_glowing_dict = self.glow_dict[self._profilename[0]]
                color_marker = player_glowing_dict[0]
                color_marker = max(-999.0, min(color_marker, 50.0))

                highlight_marker = float(player_glowing_dict[1])
                highlight_marker = max(-999.0, min(highlight_marker, 50.0))

                stabilize_color = int(player_glowing_dict[2]) > 0
                stabilize_highlight = int(player_glowing_dict[3]) > 0
                self._color, self._highlight = \
                    _profile.get_player_profile_colors(
                        self._profilename,
                        profiles=self._profiles)

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
        except KeyError:
            self.character_index = self._random_character_index
            self._color = self._random_color
            self._highlight = self._random_highlight

        self._update_icon()
        self._update_text()
