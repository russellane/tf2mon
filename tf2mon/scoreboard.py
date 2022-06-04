"""Two-Team Scoreboard."""

import curses
from collections import namedtuple

import libcurses

from tf2mon.hacker import HackerAttr


class Scoreboard:
    """Two-Team Scoreboard."""

    # pylint: disable=too-many-instance-attributes

    Column = namedtuple(
        "Column",
        [
            "width",
            "th",  # format when building heading line
            "td",  # format when building detail line
            "heading",
        ],
    )

    _columns_user = [
        Column(10, "{:>10}", "{:>10}", "STEAMID"),
        Column(1, "{:1}", "{:1}", "C"),
        Column(3, "{:>3}", "{:>3}", "K"),
        Column(3, "{:>3}", "{:>3}", "D"),
        Column(4, "{:>4}", "{:4.1f}", "KD"),
        Column(3, "{:>3}", "{:>3}", "SNI"),
        Column(1, "{:1}", "{:1}", "S"),
        Column(4, "{:>4}", "{:>4}", "UID"),
        Column(25, "{:25}", "{:25}", "USERNAME"),
    ]

    _columns_steamplayer = [
        Column(20, "{:20}", "{:20}", "PERSONANAME"),
        Column(20, "{:20}", "{:20}", "REALNAME"),
        Column(1, "{:1}", "{:1}", "P"),
        Column(2, "{:2}", "{:2}", "CC"),
        Column(2, "{:2}", "{:2}", "SC"),
        Column(4, "{:4}", "{:4}", "CI"),
        Column(0, "{}", "{}", "AGE"),
    ]

    _columns = _columns_user + _columns_steamplayer

    def __init__(self, monitor, win1, color1, win2, color2):
        """Create scoreboard for two teams.

        Args:
            monitor:    the monitor.
            win1:       curses window for team 1
            color1:     base color for team 2
            win2:       curses window for team 2
            color2:     base color for team 2
        """

        # pylint: disable=too-many-arguments

        self.monitor = monitor
        self.win1 = win1
        self.color1 = color1
        self.win2 = win2
        self.color2 = color2

        self._formatted_header = None
        self._fmt_user = None
        self._fmt_steamplayer = None

        # build the format string to build the header now
        fmt = " ".join([x.th for x in self._columns])

        # build the header now
        self._formatted_header = fmt.format(*[x.heading for x in self._columns])

        # build the format string to build detail lines later
        self._fmt_user = " ".join([x.td for x in self._columns_user])

        # build the format string to build detail lines later
        self._fmt_steamplayer = " ".join([x.td for x in self._columns_steamplayer])

        # calculate each column's x-ordinate for lookup by `heading`.
        self._col_x_width_by_heading = {}
        i = 0
        for col in self._columns:
            self._col_x_width_by_heading[col.heading] = (i, col.width)
            i += col.width + 1

        # updated by `set_sort_order`
        self._sort_col_x = 0
        self._sort_col_width = 0

    def set_sort_order(self, sort_order):
        """Set sort order."""

        self._sort_col_x, self._sort_col_width = self._col_x_width_by_heading[sort_order.name]

    def show_scores(self, team1, team2):
        """Display the scoreboards."""

        libcurses.clear_mouse_handlers()

        # Fill in whatever space is left on the scoreboards with users
        # whose team is unknown; doesn't matter which side they're
        # displayed on.
        unassigned = [x for x in self.monitor.users.active_users() if not x.team]

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
            line = self._fmt_user.format(
                user.steamid.id if user.steamid else 0,
                user.role.display,
                user.nkills,
                user.ndeaths,
                user.kdratio,
                user.nsnipes,
                user.n_status_checks,
                user.userid,
                user.username,
            )
            if user.perk:
                line += " +" + user.perk
            elif _sp := user.steamplayer:
                line += " " + self._fmt_steamplayer.format(
                    _sp.personaname
                    if (_sp.personaname and _sp.personaname != user.username)
                    else "",
                    _sp.realname or "",
                    _sp.personastate or "",
                    _sp.loccountrycode or "",
                    _sp.locstatecode or "",
                    _sp.loccityid or "",
                    _sp.age or "",
                )

            try:
                win.addnstr(lineno, 0, line, ncols, self.monitor.ui.user_color(user, color))
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

        for active_user in self.monitor.users.active_users():
            active_user.selected = False
        user.selected = True
        self.monitor.ui.update_display()

        if mouse.nclicks == 2:
            user.kick(HackerAttr.CHEATER)
        elif mouse.nclicks == 3:
            user.kick(HackerAttr.RACIST)

        return True  # handled
