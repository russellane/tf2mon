"""User Interface module."""

import contextlib
import curses
import sys
import time
from enum import Enum

import libcurses
from loguru import logger

from tf2mon.scoreboard import Scoreboard
from tf2mon.toggle import Toggle
from tf2mon.user import Team, UserState

# from playsound import playsound


# These would have been defined within class UI (because they're only used internally)
# but `pydoc` doesn't display their values when defined there; it does when defined here.

GRID_LAYOUT = Enum("_grid_layout_enum", "WIDE TALL")
GRID_LAYOUT.__doc__ = "Grid layout."

USER_PANEL = Enum("_user_panel_enum", "AUTO DUELS KICKS SPAMS")
USER_PANEL.__doc__ = "What to display in the user window"

LOG_LOCATION = Enum("_log_location_enum", "MOD FILE THREAD NOLOC")
LOG_LOCATION.__doc__ = (
    "How to format the location field of messages displayed in the logger window."
)

SORT_ORDER = Enum("_so", "STEAMID K KD USERNAME")
SORT_ORDER.__doc__ = "Column to sort the scoreboard by."


class UI:
    """User Interface class."""

    # pylint: disable=too-many-instance-attributes

    _log_locations = {
        LOG_LOCATION.MOD: "{module}:{line}",
        LOG_LOCATION.FILE: "{file}:{line}:{function}",
        LOG_LOCATION.THREAD: "{thread.name}:{file}:{line}:{function}",
        LOG_LOCATION.NOLOC: None,
    }

    def __init__(self, monitor, win: curses.window):
        """Initialize User Interface instance.

        Args:
            monitor:    `TF2Monitor` instance.
            win:        curses window to use; likely `stdscr`.
        """

        self.monitor = monitor
        self.max_users = 32

        # create empty grid
        self.grid = libcurses.Grid(win)

        # promote some grid methods.
        self.redraw = self.grid.redraw
        self.refresh = self.grid.refresh

        # `self._build_grid` creates these windows, sized to fill `win`.
        self.chatwin_blu: curses.window = None
        self.chatwin_red: curses.window = None
        self.scorewin_blu: curses.window = None
        self.scorewin_red: curses.window = None
        self.user_win: curses.window = None
        self.logger_win: curses.window = None
        self.status_win: curses.window = None
        self.cmdline_win: curses.window = None

        # the windows may be placed in different arrangements.
        self.grid_layout = Toggle("_grid_layout", GRID_LAYOUT)
        self.grid_layout.start(GRID_LAYOUT.WIDE)
        self._build_grid_layouts = {
            GRID_LAYOUT.WIDE: self._build_grid_layout_wide,
            GRID_LAYOUT.TALL: self._build_grid_layout_tall,
        }
        self._do_build_grid = self._build_grid_layouts[self.grid_layout.value]

        # `register_builder` 1) calls `_build_grid` and 2) configures
        # `KEY_RESIZE` to call it again each time that event occurs.
        self.grid.register_builder(self._build_grid)

        #
        self.monitor.fkeys.register_curses_handlers()

        #
        self._curses_logwin = libcurses.LoggerWindow(self.logger_win)
        self._curses_logwin.set_verbose(self.monitor.options.verbose)
        self.colormap = self._curses_logwin.colormap

        #
        self._scoreboard = Scoreboard(
            self.monitor,
            self.scorewin_blu,
            self.colormap[Team.BLU.name],
            self.scorewin_red,
            self.colormap[Team.RED.name],
        )

        #
        self.debug_flag = Toggle("_df", [False, True])
        self.taunt_flag = Toggle("_tf", [False, True])
        self.throe_flag = Toggle("_gf", [True, False])

        # control contents of user window
        self.user_panel = Toggle("_up", USER_PANEL)

        # options when displaying USER_PANEL.USER
        self.show_duels = Toggle("_sd", [True, False])
        self.show_actions = Toggle("_sa", [True, False])
        self.show_chats = Toggle("_sc", [False, True])

        # how to format the location field of messages displayed in the logger window.
        self.log_location = Toggle("_ll", LOG_LOCATION)
        self.log_location.start(LOG_LOCATION.MOD)
        self._curses_logwin.set_location(self._log_locations[self.log_location.value])

        # if to show kd ratio in User.moniker.
        self.show_kd = Toggle("_kd", [False, True])

        # how to sort users in the scoreboard.
        self.sort_order = Toggle("_so", SORT_ORDER)
        self.sort_order.start(SORT_ORDER.KD)
        self.set_sort_order(self.sort_order.value)

        #
        self.notify_operator = False
        self.sound_alarm = False

    def cycle_grid_layout(self):
        """Cycle through grid layouts."""

        self._do_build_grid = self._build_grid_layouts[self.grid_layout.cycle]
        self._build_grid()

    def _build_grid(self):
        """Add boxes to grid.

        Called at init, on KEY_RESIZE events, and when grid_layout is cycled.
        """

        try:
            self._do_build_grid()
        except AssertionError:
            curses.endwin()
            logger.error("Terminal too small; try `Maximize` and `Ctrl+Minus`.")
            sys.exit(0)

        #
        self.chatwin_blu.scrollok(True)
        self.chatwin_red.scrollok(True)
        self.scorewin_blu.scrollok(False)
        self.scorewin_red.scrollok(False)
        self.user_win.scrollok(True)
        self.logger_win.scrollok(True)
        self.status_win.scrollok(False)
        self.cmdline_win.scrollok(True)
        #
        self.cmdline_win.keypad(True)
        #
        self.redraw()

    def _build_grid_layout_wide(self):
        """Horizontal layout.

        +-------------------+----------------------+
        | chatwin_blu       | chatwin_red          |  section 1
        |                   |                      |
        +-------------------+----------------------+
        | scorewin_blu      | scorewin_red         |  section 2
        |                   |                      |
        +--------------+----+----------------------+
        | user_win     | logger_win                |  section 3
        |              |                           |
        +--------------+--------+------------------+
        | status_win            | cmdline_win      |  section 4
        +-----------------------+------------------+
        """

        # section 1
        self.chatwin_blu = self.grid.box(
            "chatwin_blu",
            nlines=10,
            ncols=int(self.grid.ncols / 2),
            left=self.grid,
            top=self.grid,
        )

        self.chatwin_red = self.grid.box(
            "chatwin_red",
            nlines=0,
            ncols=0,
            left2r=self.chatwin_blu,
            right=self.grid,
            top=self.chatwin_blu,
            bottom=self.chatwin_blu,
        )

        # section 2
        self.scorewin_blu = self.grid.box(
            "scorewin_blu",
            nlines=int(self.max_users / 2) + 2 + 1,  # 2=borders (top and bottom), 1=header.
            ncols=int(self.grid.ncols / 2),
            left=self.grid,
            top2b=self.chatwin_blu,
        )

        self.scorewin_red = self.grid.box(
            "scorewin_red",
            nlines=0,
            ncols=0,
            left2r=self.scorewin_blu,
            right=self.grid,
            top=self.scorewin_blu,
            bottom=self.scorewin_blu,
        )

        # section 4
        self.status_win = self.grid.box(
            "status",
            nlines=3,
            ncols=int(2 * self.grid.ncols / 3),
            left=self.grid,
            bottom=self.grid,
        )

        self.cmdline_win = self.grid.box(
            "cmdline",
            nlines=3,
            ncols=0,
            left2r=self.status_win,
            right=self.grid,
            bottom=self.grid,
        )

        # section 3 - fills gap between sections 2 and 4
        self.user_win = self.grid.box(
            "user",
            nlines=0,
            ncols=int(self.grid.ncols / 3),
            left=self.grid,
            top2b=self.scorewin_blu,
            bottom2t=self.status_win,
        )

        self.logger_win = self.grid.box(
            "logwin",
            nlines=0,
            ncols=0,
            left2r=self.user_win,
            right=self.grid,
            top=self.user_win,
            bottom=self.user_win,
        )

    def _build_grid_layout_tall(self):
        """Vertical layout.

        +-------------------+----------------------+
        | scorewin_blu      | chatwin_blu          |  section 1
        |                   |                      |
        +-------------------+----------------------+
        | scorewin_red      | chatwin_red          |  section 2
        |                   |                      |
        +--------------+----+----------------------+
        | user_win     | logger_win                |  section 3
        |              |                           |
        +--------------+--------+------------------+
        | status_win            | cmdline_win      |  section 4
        +-----------------------+------------------+
        """

        # 124=len(self._scoreboard._formatted_header) + 2=borders (left and right) + 1=padding

        width = min(124, int(2 * self.grid.ncols / 3))

        # section 1
        self.scorewin_blu = self.grid.box(
            "scorewin_blu",
            nlines=int(self.max_users / 2) + 2 + 1,  # 2=borders (top and bottom), 1=header.
            ncols=width,
            left=self.grid,
            top=self.grid,
        )

        self.chatwin_blu = self.grid.box(
            "chatwin_blu",
            nlines=0,
            ncols=0,
            left2r=self.scorewin_blu,
            right=self.grid,
            top=self.scorewin_blu,
            bottom=self.scorewin_blu,
        )

        # section 2
        self.scorewin_red = self.grid.box(
            "scorewin_red",
            nlines=int(self.max_users / 2) + 2 + 1,  # 2=borders (top and bottom), 1=header.
            ncols=width,
            left=self.grid,
            top2b=self.scorewin_blu,
        )

        self.chatwin_red = self.grid.box(
            "chatwin_red",
            nlines=0,
            ncols=0,
            left2r=self.scorewin_red,
            right=self.grid,
            top=self.scorewin_red,
            bottom=self.scorewin_red,
        )

        # section 4
        self.status_win = self.grid.box(
            "status",
            nlines=3,
            ncols=int(2 * self.grid.ncols / 3),
            left=self.grid,
            bottom=self.grid,
        )

        self.cmdline_win = self.grid.box(
            "cmdline",
            nlines=3,
            ncols=0,
            left2r=self.status_win,
            right=self.grid,
            bottom=self.grid,
        )

        # section 3 - fills gap between sections 2 and 4
        self.user_win = self.grid.box(
            "user",
            nlines=0,
            ncols=int(self.grid.ncols / 3),
            left=self.grid,
            top2b=self.scorewin_red,
            bottom2t=self.status_win,
        )

        self.logger_win = self.grid.box(
            "logwin",
            nlines=0,
            ncols=0,
            left2r=self.user_win,
            right=self.grid,
            top=self.user_win,
            bottom=self.user_win,
        )

    def cycle_log_location(self):
        """Cycle format of location in messages displayed in logger window."""

        self._curses_logwin.set_location(self._log_locations[self.log_location.cycle])

    def set_sort_order(self, sort_order):
        """Set scoreboard sort column."""

        self.monitor.users.set_sort_order(sort_order)
        self._scoreboard.set_sort_order(sort_order)

    def getline(self, prompt=None):
        """Read and return next line from keyboard."""

        self.cmdline_win.erase()

        if prompt:
            self.cmdline_win.addstr(0, 0, prompt)
            self.cmdline_win.noutrefresh()

        return libcurses.getline(self.cmdline_win)

    def update_display(self):
        """Update display."""

        if self.sound_alarm:
            self.sound_alarm = False
            if self.monitor.conlog.is_eof:  # don't do this when replaying logfile from start
                # playsound('/usr/share/sounds/sound-icons/prompt.wav')
                # playsound('/usr/share/sounds/sound-icons/cembalo-10.wav')
                curses.flash()
                # curses.beep()

        #
        if self.user_panel.value == USER_PANEL.KICKS or (
            self.user_panel.value == USER_PANEL.AUTO and self.monitor.kicks.msgs
        ):
            self._show_lines("KICKS", reversed(self.monitor.kicks.msgs), self.user_win)
        #
        elif self.user_panel.value == USER_PANEL.SPAMS or (
            self.user_panel.value == USER_PANEL.AUTO and self.monitor.spams.msgs
        ):
            self._show_lines("SPAMS", reversed(self.monitor.spams.msgs), self.user_win)
        #
        else:
            self._show_user(self.monitor.me)

        # chatwin_blu and chatwin_red are rendered from gameplay/_playerchat

        #
        self._scoreboard.show_scores(
            team1=list(self.monitor.users.active_team_users(Team.BLU)),
            team2=list(self.monitor.users.active_team_users(Team.RED)),
        )

        #
        self.show_status()

        #
        self.refresh()

    def user_color(self, user, color):
        """Return `color` to display `user` in scoreboard."""

        if user.display_level:
            color = self.colormap[user.display_level]

        if user == self.monitor.my.last_killer:
            color |= curses.A_BOLD | curses.A_ITALIC

        if user == self.monitor.my.last_victim:
            color |= curses.A_BOLD

        if user.selected:
            color |= curses.A_REVERSE

        if not user.team:
            color |= curses.A_UNDERLINE

        if user.cloner:
            color |= curses.A_BLINK

        return color

    def show_chat(self, chat):
        """Display (append) `chat` in appropriate team window."""

        line = f"{chat.seqno}: {chat.user.username:20.20}: {chat.msg}"

        win = self.chatwin_blu if chat.user.team == Team.BLU else self.chatwin_red
        color = self.colormap[chat.user.team.name if chat.user.team else "user"]
        if chat.teamflag:
            color |= curses.A_UNDERLINE

        if sum(win.getyx()):
            win.addch("\n")
        win.addstr(line, self.user_color(chat.user, color))
        win.noutrefresh()

    def clear_chats(self):
        """Clear the chat windows."""

        now = time.asctime()
        for win in (self.chatwin_blu, self.chatwin_red):
            win.erase()
            win.addstr(now)

    #    def _show_chats(self, chats):
    #
    #        blu, red = [], []
    #
    #        for chat in chats:
    #            s = f'{chat.seqno}: {chat.user.username:.20}: {chat.msg}\n'
    #            if chat.team == Team.BLU:
    #                blu.append(s)
    #            else:
    #                red.append(s)
    #
    #        self._show_lines('BLU', blu, self.chatwin_blu)
    #        self._show_lines('RED', red, self.chatwin_red)

    def _show_user(self, user):

        lines = []
        indent = " " * 12  # 12=len("99 and 99 vs")

        lines.append("Duels:")
        for opponent in [x for x in user.opponents.values() if x.state == UserState.ACTIVE]:
            lines.append(f"{user.duel_as_str(opponent, True)} vs {opponent.moniker}")

            if opponent.key in user.nkills_by_opponent_by_weapon:
                for weapon, count in user.nkills_by_opponent_by_weapon[opponent.key].items():
                    lines.append(f"{indent} K {count:2} {weapon}")

            if user.key in opponent.nkills_by_opponent_by_weapon:
                for weapon, count in opponent.nkills_by_opponent_by_weapon[user.key].items():
                    lines.append(f"{indent} D {count:2} {weapon}")

        if self.show_actions.value:
            lines.extend(user.actions)

        if self.show_chats.value:
            lines.extend([x.msg for x in user.chats])

        self._show_lines("user", lines, self.user_win)

    def show_status(self):
        """Update status line."""

        line = self.monitor.fkeys.get_status_line() + f" UID={self.monitor.my.userid}"

        try:
            self.status_win.addstr(
                0, 0, line, self.colormap["NOTIFY" if self.notify_operator else "STATUS"]
            )
            self.status_win.clrtoeol()
        except curses.error:
            pass
        self.status_win.noutrefresh()

    def _show_lines(self, level, lines, win):

        win.erase()

        for line in lines:
            with contextlib.suppress(curses.error):
                win.addstr(line + "\n", self.colormap[level])

    def show_help(self):
        """Show help."""

        motd = self.monitor.tf2_cfg_dir / "motd.txt"
        logger.log("help", f" {motd} ".center(80, "-"))

        with open(motd, encoding="utf-8") as file:
            for line in file:
                logger.log("help", line.strip())
