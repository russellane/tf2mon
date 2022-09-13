"""Scoreboard."""

import curses

import libcurses

import tf2mon
from tf2mon.player import Player
from tf2mon.texttable import TextColumn, TextTable
from tf2mon.user import Team
from tf2mon.users import Users


class Scoreboard:
    """Scoreboard."""

    table = TextTable(
        [
            TextColumn(-5, "UID"),
            TextColumn(1, "P"),
            TextColumn(2, "CC"),
            TextColumn(2, "SC"),
            # TextColumn(4, "CI"),
            TextColumn(-4, "AGE"),
            TextColumn(-10, "STEAMID"),
            TextColumn(-8, "CONN"),
            TextColumn(1, "S"),
            TextColumn(-3, "SNI"),
            TextColumn(-3, "K"),
            TextColumn(-3, "D"),
            TextColumn(4.1, "KD"),
            TextColumn(8, "CLASS"),
            TextColumn(25, "USERNAME"),
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

        # calculate each column's x-ordinate for lookup by `heading`.
        self._col_x_width_by_heading = {}
        i = 0
        for col in self.table.columns:
            self._col_x_width_by_heading[col.heading] = (i, col.width)
            i += col.width + 1

        # updated by `set_sort_order`
        self._sort_col_x = 0
        self._sort_col_width = 0

    def set_sort_order(self, sort_order):
        """Set sort order."""

        self._sort_col_x, self._sort_col_width = self._col_x_width_by_heading[sort_order]

    def refresh(self) -> None:
        """Display the scoreboards."""

        libcurses.clear_mouse_handlers()

        users = list(Users.sorted())
        team1 = [x for x in users if x.team == Team.BLU]
        team2 = [x for x in users if x.team == Team.RED]

        # Fill in whatever space is left on the scoreboards with users
        # whose team is unknown; doesn't matter which side they're
        # displayed on.
        unassigned = [x for x in users if not x.team]
        nusers = self.win1.getmaxyx()[0] - 1
        while len(team1) < nusers and len(unassigned) > 0:
            team1.append(unassigned.pop(0))

        self._refresh_team(self.win1, self.color1, team1)
        self._refresh_team(self.win2, self.color2, team2 + unassigned)

    def _refresh_team(self, win, color, team):

        ncols = win.getmaxyx()[1]
        win.erase()

        # column headings
        win.addnstr(0, 0, self.table.formatted_header, ncols, color)

        # highlight heading of active sort column
        win.chgat(
            0, self._sort_col_x, self._sort_col_width, color | curses.A_BOLD | curses.A_ITALIC
        )

        for lineno, user in enumerate(team, start=1):
            if not user.username:
                continue

            if user.dirty:
                user.dirty = False

                names = [user.username]
                _sp = user.steamplayer
                if user.perk:
                    names.append(user.perk)
                elif _sp:
                    if _sp.personaname and _sp.personaname != user.username:
                        names.append(_sp.personaname)
                    if _sp.realname:
                        names.append(_sp.realname)

                user.last_scoreboard_line = self.table.format_detail(
                    user.userid,
                    (_sp and _sp.personastate) or "",
                    (_sp and _sp.loccountrycode) or "",
                    (_sp and _sp.locstatecode) or "",
                    # (_sp and _sp.loccityid) or "",
                    (_sp and _sp.age) or "",
                    user.steamid.id if user.steamid else 0,
                    user.s_elapsed,
                    user.n_status_checks,
                    user.nsnipes,
                    user.nkills,
                    user.ndeaths,
                    user.kdratio,
                    user.role.name,
                    " +".join(names),
                )

            try:
                win.addnstr(
                    lineno,
                    0,
                    user.last_scoreboard_line,
                    ncols,
                    tf2mon.ui.user_color(user, color),
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

        for active_user in Users.active_users():
            active_user.selected = False
        user.selected = True
        tf2mon.ui.update_display()

        if mouse.nclicks == 2:
            user.kick(Player.CHEATER)
        elif mouse.nclicks == 3:
            user.kick(Player.RACIST)

        return True  # handled
