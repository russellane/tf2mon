"""User Interface."""

import contextlib
import curses
import os
import sys
import textwrap
import time
from enum import Enum

import libcurses
from loguru import logger

import tf2mon.layouts
from tf2mon.scoreboard import Scoreboard
from tf2mon.toggle import Toggle
from tf2mon.user import Team, UserState

# from playsound import playsound


# These would have been defined within class UI (because they're only used internally)
# but `pydoc` doesn't display their values when defined there; it does when defined here.

USER_PANEL = Enum("_user_panel_enum", "AUTO DUELS KICKS SPAMS")
USER_PANEL.__doc__ = "Contents of user panel."

LOG_LEVEL = Enum("_lvl_enum", "INFO DEBUG TRACE")
LOG_LEVEL.__doc__ = "Logging level."

LOG_LOCATION = Enum("_loc_enum", "MOD NAM THM THN FILE NUL")
LOG_LOCATION.__doc__ = "Format of logger location field."

SORT_ORDER = Enum("_sort_order_enum", "STEAMID K KD USERNAME")
SORT_ORDER.__doc__ = "Scoreboard sort column."


class UI:
    """User Interface."""

    # pylint: disable=too-many-instance-attributes

    _log_levels = {
        LOG_LEVEL.INFO: "INFO",  # ""
        LOG_LEVEL.DEBUG: "DEBUG",  # "-v"
        LOG_LEVEL.TRACE: "TRACE",  # "-vv"
    }
    log_level = Toggle("_lvl_cycle", LOG_LEVEL)

    _log_locations = {
        LOG_LOCATION.MOD: "{module}.{function}:{line}",
        LOG_LOCATION.NAM: "{name}.{function}:{line}",
        LOG_LOCATION.THM: "{thread.name}:{module}.{function}:{line}",
        LOG_LOCATION.THN: "{thread.name}:{name}.{function}:{line}",
        LOG_LOCATION.FILE: "{file}:{function}:{line}",
        LOG_LOCATION.NUL: None,
    }
    log_location = Toggle("_loc_cycle", LOG_LOCATION)

    def __init__(self, monitor, win: curses.window):
        """Initialize User Interface."""

        self.monitor = monitor
        self.notify_operator = False
        self.sound_alarm = False

        # F2 Toggle Debug (control `say` vs `echo`).
        self.debug_flag = Toggle("_df", [False, True])

        # F3 Enable/disable Taunts and Throes.
        self.taunt_flag = Toggle("_tf", [False, True])
        self.throe_flag = Toggle("_gf", [True, False])

        # F4 Include kd-ratio in messages (`User.moniker`)
        self.show_kd = Toggle("_kd", [False, True])

        # F5 Control User-panel display: Kicks, Spams, Duels and Auto.
        self.user_panel = Toggle("_up", USER_PANEL)

        # options when displaying USER_PANEL.USER
        # self.show_actions = Toggle("_sa", [True, False])
        # if self.show_actions.value:
        #     lines.extend(user.actions)

        # Scoreboard sort column.
        self.sort_order = Toggle("_so", SORT_ORDER)
        self.sort_order.start(SORT_ORDER.KD)

        # create empty grid
        self.grid = libcurses.Grid(win)

        # `self.build_grid` creates these windows, sized to fill `win`.
        self.chatwin_blu: curses.window = None
        self.chatwin_red: curses.window = None
        self.scorewin_blu: curses.window = None
        self.scorewin_red: curses.window = None
        self.user_win: curses.window = None
        self.kicks_win: curses.window = None
        self.spams_win: curses.window = None
        self.duels_win: curses.window = None
        self.logger_win: curses.window = None
        self.status_win: curses.window = None
        self.cmdline_win: curses.window = None

        # the windows may be placed in different arrangements.
        self.grid_layout = Toggle("_grid_layout", tf2mon.layouts.LAYOUT_ENUM)
        self.grid_layout.start(self.monitor.options.layout)

        # `register_builder` 1) calls `build_grid` and 2) configures
        # `KEY_RESIZE` to call it again each time that event occurs.
        self.grid.register_builder(self.build_grid)

        #
        self.logsink = libcurses.Sink(self.logger_win)
        #
        self.logsink.set_verbose(self.monitor.options.verbose)
        self.log_level.start(LOG_LEVEL.__dict__[self.logsink.level])
        #
        self.log_location.start(LOG_LOCATION.MOD)
        self.logsink.set_location(self._log_locations[self.log_location.value])

        self.colormap = libcurses.get_colormap()
        #
        self._scoreboard = Scoreboard(
            self.monitor,
            self.scorewin_blu,
            self.colormap[Team.BLU.name],
            self.scorewin_red,
            self.colormap[Team.RED.name],
        )

        self.set_sort_order(self.sort_order.value)

    def cycle_grid_layout(self):
        """Use next grid layout."""

        _ = self.grid_layout.cycle

        # self.grid.boxes = self.grid.boxes[:1]
        self.grid.handle_term_resized_event()
        self.show_status()

    def build_grid(self):
        """Add boxes to grid.

        Called at init, on KEY_RESIZE events, and when layout changes.
        """

        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements

        klass = tf2mon.layouts.LAYOUT_CLASSES[self.grid_layout.value]
        try:
            layout = klass(self.grid)
        except AssertionError:
            curses.endwin()
            msg = "Terminal too small; try `Maximize` and `Ctrl+Minus`."
            logger.error(msg)
            if not os.isatty(sys.stderr.fileno()):
                print(f"ERROR: {msg}")
            sys.exit(1)

        if os.isatty(sys.stderr.fileno()):
            os.close(sys.stderr.fileno())

        if not layout.logger_win:
            raise RuntimeError(f"undefined `logger_win` in {layout}.")
        if not layout.status_win:
            raise RuntimeError(f"undefined `status_win` in {layout}.")
        if not layout.cmdline_win:
            raise RuntimeError(f"undefined `cmdline_win` in {layout}.")

        # promote
        self.chatwin_blu = layout.chatwin_blu
        self.chatwin_red = layout.chatwin_red
        self.scorewin_blu = layout.scorewin_blu
        self.scorewin_red = layout.scorewin_red
        self.user_win = layout.user_win
        self.kicks_win = layout.kicks_win
        self.spams_win = layout.spams_win
        self.duels_win = layout.duels_win
        self.logger_win = layout.logger_win
        self.status_win = layout.status_win
        self.cmdline_win = layout.cmdline_win

        if self.chatwin_blu:
            self.chatwin_blu.scrollok(True)
        if self.chatwin_red:
            self.chatwin_red.scrollok(True)
        if self.scorewin_blu:
            self.scorewin_blu.scrollok(False)
        if self.scorewin_red:
            self.scorewin_red.scrollok(False)
        if self.user_win:
            self.user_win.scrollok(False)
        if self.kicks_win:
            self.kicks_win.scrollok(False)
        if self.spams_win:
            self.spams_win.scrollok(False)
        if self.duels_win:
            self.duels_win.scrollok(False)
        if self.logger_win:
            self.logger_win.scrollok(True)
        if self.status_win:
            self.status_win.scrollok(False)
        if self.cmdline_win:
            self.cmdline_win.scrollok(True)
            self.cmdline_win.keypad(True)

        self.grid.redraw()

    def cycle_log_level(self) -> None:
        """Cycle logging level in logger window."""

        self.logsink.set_level(self._log_levels[self.log_level.cycle])

    def cycle_log_location(self) -> None:
        """Cycle format of location in messages displayed in logger window."""

        self.logsink.set_location(self._log_locations[self.log_location.cycle])

    def set_sort_order(self, sort_order):
        """Set scoreboard sort column."""

        self.monitor.users.set_sort_order(sort_order)
        self._scoreboard.set_sort_order(sort_order)

    def getline(self, prompt=None):
        """Read and return next line from keyboard."""

        self.cmdline_win.erase()
        if prompt:
            self.cmdline_win.addstr(0, 0, prompt)
        return libcurses.getline(self.cmdline_win)

    def update_display(self):
        """Update display."""

        if self.sound_alarm:
            self.sound_alarm = False
            if self.monitor.conlog.is_eof:  # don't do this when replaying logfile from start
                ...
                # playsound('/usr/share/sounds/sound-icons/prompt.wav')
                # playsound('/usr/share/sounds/sound-icons/cembalo-10.wav')
                # curses.flash()
                # curses.beep()

        self.refresh_kicks()
        self.refresh_spams()
        self.refresh_duels(self.monitor.me)
        self.refresh_user(self.monitor.me)
        # chatwin_blu and chatwin_red are rendered from gameplay/_playerchat
        self._scoreboard.show_scores(
            team1=list(self.monitor.users.active_team_users(Team.BLU)),
            team2=list(self.monitor.users.active_team_users(Team.RED)),
        )
        self.show_status()
        self.grid.refresh()

    def refresh_kicks(self):
        """Refresh kicks panel."""

        if self.kicks_win:
            # ic(self.kicks_win.getbegyx())
            # ic(self.kicks_win.getmaxyx())
            self._show_lines("KICKS", reversed(self.monitor.kicks.msgs), self.kicks_win)

        # if self.user_win:
        #     self.refresh_user(self.monitor.me)

    def refresh_spams(self):
        """Refresh spams panel."""

        if self.spams_win:
            self._show_lines("SPAMS", reversed(self.monitor.spams.msgs), self.spams_win)

        if self.user_win:
            self.refresh_user(self.monitor.me)

    def refresh_duels(self, user):
        """Refresh duels panel."""

        if self.duels_win:
            self._show_lines("user", self._format_duels(user), self.duels_win)

        if self.user_win:
            self.refresh_user(self.monitor.me)

    def refresh_user(self, user):
        """Refresh user panel."""

        if self.user_win:
            if self.user_panel.value == USER_PANEL.KICKS or (
                self.user_panel.value == USER_PANEL.AUTO and self.monitor.kicks.msgs
            ):
                self._show_lines(
                    "KICKS",
                    reversed(self.monitor.kicks.msgs)
                    if self.monitor.kicks.msgs
                    else ["No Kicks"],
                    self.user_win,
                )
            #
            elif self.user_panel.value == USER_PANEL.SPAMS or (
                self.user_panel.value == USER_PANEL.AUTO and self.monitor.spams.msgs
            ):
                self._show_lines(
                    "SPAMS",
                    reversed(self.monitor.spams.msgs)
                    if self.monitor.spams.msgs
                    else ["No Spams"],
                    self.user_win,
                )
            #
            else:
                self._show_lines("user", self._format_duels(user), self.user_win)

            self.user_win.noutrefresh()

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
            color |= curses.A_ITALIC

        return color

    def show_chat(self, chat):
        """Display (append) `chat` in appropriate team window."""

        win = None
        if chat.user.team == Team.RED:
            win = self.chatwin_red
        if not win:
            win = self.chatwin_blu  # unassigned, or RED in shared window.
        if not win:
            return  # not showing chats

        color = self.colormap[chat.user.team.name if chat.user.team else "user"]
        if chat.teamflag:
            color |= curses.A_UNDERLINE

        if sum(win.getyx()):
            win.addch("\n")
        line = f"{chat.seqno}: {chat.user.username:20.20}: {chat.msg}"
        win.addstr(line, self.user_color(chat.user, color))
        win.noutrefresh()

    def clear_chats(self):
        """Clear the chat windows."""

        now = time.asctime()
        for win in [x for x in (self.chatwin_blu, self.chatwin_red) if x]:
            win.erase()
            win.addstr(now)

    def _format_duels(self, user):

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

        return lines

    def show_status(self):
        """Update status line."""

        line = self.monitor.commands.get_status_line() + f" UID={self.monitor.my.userid}"

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

        with contextlib.suppress(curses.error):
            for line in lines:
                win.addstr(line + "\n", self.colormap[level])
        win.noutrefresh()

    def show_help(self):
        """Show help."""

        for line in (
            textwrap.dedent(
                """
    Press Enter to process next line.
    Enter "b 500" to set breakpoint at line 500.
    Enter "/pattern[/i]" to set search pattern.
    Enter "/" to clear search pattern.
    Enter "c" to continue.
    Enter "quit" or press ^D to quit."
                """
            )
            .strip()
            .splitlines()
        ):
            logger.log("help", line)

    def show_motd(self):
        """Show message of the day."""

        motd = self.monitor.tf2_scripts_dir.parent / "motd.txt"
        logger.log("help", f" {motd} ".center(80, "-"))

        with open(motd, encoding="utf-8") as file:
            for line in file:
                logger.log("help", line.strip())

    def show_debug(self):
        """Debug grid."""

        logger.debug(self.grid)
        for box in self.grid.boxes:
            logger.debug(self.grid.winyx(box))
