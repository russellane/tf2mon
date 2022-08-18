"""Two-Team Scoreboard."""

import curses

import libcurses

import tf2mon
from tf2mon.player import Player
from tf2mon.texttable import TextColumn, TextTable


class Scoreboard:
    """Two-Team Scoreboard."""

    # pylint: disable=too-many-instance-attributes

    _table_user = TextTable(
        [
            TextColumn(-10, "STEAMID"),
            TextColumn(1, "C"),
            TextColumn(-3, "K"),
            TextColumn(-3, "D"),
            TextColumn(4.1, "KD"),
            TextColumn(-3, "SNI"),
            TextColumn(1, "S"),
            TextColumn(-4, "UID"),
            TextColumn(-8, "CONN"),
            TextColumn(25, "USERNAME"),
        ]
    )

    _table_steamplayer = TextTable(
        [
            TextColumn(-4, "AGE"),
            TextColumn(1, "P"),
            TextColumn(2, "CC"),
            TextColumn(2, "SC"),
            # TextColumn(4, "CI"),
            TextColumn(0, "REALNAME"),
        ]
    )

    def __init__(self, win1, color1, win2, color2):
        """Create scoreboard for two teams.

        Args:
            win1:       curses window for team 1
            color1:     base color for team 2
            win2:       curses window for team 2
            color2:     base color for team 2
        """

        self.win1 = win1
        self.color1 = color1
        self.win2 = win2
        self.color2 = color2

        self._formatted_header = None
        self._fmt_user = None
        self._fmt_steamplayer = None

        self._formatted_header = " ".join(
            [
                self._table_user.formatted_header,
                self._table_steamplayer.formatted_header,
            ]
        )

        # calculate each column's x-ordinate for lookup by `heading`.
        self._col_x_width_by_heading = {}
        i = 0
        for col in self._table_user.columns + self._table_steamplayer.columns:
            self._col_x_width_by_heading[col.heading] = (i, col.width)
            i += col.width + 1

        # updated by `set_sort_order`
        self._sort_col_x = 0
        self._sort_col_width = 0

    def set_sort_order(self, sort_order):
        """Set sort order."""

        self._sort_col_x, self._sort_col_width = self._col_x_width_by_heading[sort_order]

    def show_scores(self, team1, team2):
        """Display the scoreboards."""

        libcurses.clear_mouse_handlers()

        # Fill in whatever space is left on the scoreboards with users
        # whose team is unknown; doesn't matter which side they're
        # displayed on.
        unassigned = [x for x in tf2mon.monitor.users.active_users() if not x.team]

        #
        nusers = self.win1.getmaxyx()[0] - 1
        while len(team1) < nusers and len(unassigned) > 0:
            team1.append(unassigned.pop(0))
        self._show_team_scores(self.win1, self.color1, team1)

        #
        self._show_team_scores(self.win2, self.color2, team2 + unassigned)

    def _show_team_scores(self, win, color, team):

        ncols = win.getmaxyx()[1]
        win.erase()

        # column headings
        win.addnstr(0, 0, self._formatted_header, ncols, color)

        # highlight heading of active sort column
        win.chgat(
            0, self._sort_col_x, self._sort_col_width, color | curses.A_BOLD | curses.A_ITALIC
        )

        for lineno, user in enumerate(team, start=1):
            if not user.username:
                continue

            if user.dirty:
                user.dirty = False
                user.last_scoreboard_line = self._table_user.format_detail(
                    user.steamid.id if user.steamid else 0,
                    user.role.display,
                    user.nkills,
                    user.ndeaths,
                    user.kdratio,
                    user.nsnipes,
                    user.n_status_checks,
                    user.userid,
                    user.s_elapsed,
                    user.username,
                )
                if user.perk:
                    user.last_scoreboard_line += " +" + user.perk
                elif _sp := user.steamplayer:
                    names = []
                    if _sp.personaname and _sp.personaname != user.username:
                        names.append(_sp.personaname)
                    if _sp.realname:
                        names.append(_sp.realname)
                    user.last_scoreboard_line += " " + self._table_steamplayer.format_detail(
                        _sp.age or "",
                        _sp.personastate or "",
                        _sp.loccountrycode or "",
                        _sp.locstatecode or "",
                        # _sp.loccityid or "",
                        " ".join(names),
                    )

            try:
                win.addnstr(
                    lineno,
                    0,
                    user.last_scoreboard_line,
                    ncols,
                    tf2mon.monitor.ui.user_color(user, color),
                )
            except curses.error:
                break

            # register to handle mouse events on the user.
            begin_y, begin_x = win.getbegyx()
            libcurses.add_mouse_handler(
                self._onmouse, begin_y + lineno, begin_x + 0, ncols, user
            )

    def _onmouse(self, mouse: libcurses.MouseEvent, user):
        """Handle mouse events within team scoreboards."""

        if mouse.button != 1:
            return False  # not handled

        for active_user in tf2mon.monitor.users.active_users():
            active_user.selected = False
        user.selected = True
        tf2mon.monitor.ui.update_display()

        if mouse.nclicks == 2:
            user.kick(Player.CHEATER)
        elif mouse.nclicks == 3:
            user.kick(Player.RACIST)

        return True  # handled
