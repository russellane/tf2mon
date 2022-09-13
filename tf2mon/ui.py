"""User Interface."""

import contextlib
import curses
import os
import sys

import libcurses
from loguru import logger

import tf2mon
from tf2mon.baselayout import BaseLayout
from tf2mon.scoreboard import Scoreboard
from tf2mon.user import Team, UserState
from tf2mon.users import Users

# from playsound import playsound


class UI:
    """User Interface."""

    def __init__(self, win: curses.window):
        """Initialize User Interface."""

        self.notify_operator = False
        self.sound_alarm = False

        # create empty grid
        self.grid = libcurses.Grid(win)

        self.layout: BaseLayout = None  # set by `build_grid`.

        # `register_builder` 1) calls `build_grid` and 2) configures
        # `KEY_RESIZE` to call it again each time that event occurs.
        self.grid.register_builder(self.build_grid)

        # begin logging to curses window, too.
        self.logsink = libcurses.Sink(self.layout.logger_win)

        # map of `loguru-level-name` to `curses-color/attr`.
        self.colormap = libcurses.get_colormap()

        #
        self.scoreboard = Scoreboard(
            self.layout.scorewin_blu,
            self.colormap[Team.BLU.name],
            self.layout.scorewin_red,
            self.colormap[Team.RED.name],
        )

    def build_grid(self) -> None:
        """Add boxes to grid.

        Called at init, on KEY_RESIZE events, and when layout changes.
        """

        klass = tf2mon.GridLayoutControl.value
        try:
            self.layout = klass(self.grid)
        except AssertionError:
            curses.endwin()
            msg = "Terminal too small; try `Maximize` and `Ctrl+Minus`."
            logger.error(msg)
            if not os.isatty(sys.stderr.fileno()):
                print(f"ERROR: {msg}")
            sys.exit(1)

        if os.isatty(sys.stderr.fileno()):
            os.close(sys.stderr.fileno())

        for attr in ["logger_win", "status_win", "cmdline_win"]:
            if not hasattr(self.layout, attr):
                raise NotImplementedError(f"undefined `{attr}` in {self.layout}.")

        for win in [
            self.layout.chatwin_blu,
            self.layout.chatwin_red,
            self.layout.logger_win,
        ]:
            if win:
                win.scrollok(True)

        for win in [
            self.layout.scorewin_blu,
            self.layout.scorewin_red,
            self.layout.user_win,
            self.layout.kicks_win,
            self.layout.spams_win,
            self.layout.duels_win,
            self.layout.status_win,
        ]:
            if win:
                win.scrollok(False)

        if self.layout.cmdline_win:
            self.layout.cmdline_win.scrollok(True)
            self.layout.cmdline_win.keypad(True)

        self.refresh_chats()
        self.grid.redraw()

    def getline(self, prompt=None):
        """Read and return next line from keyboard."""

        self.layout.cmdline_win.erase()
        if prompt:
            self.layout.cmdline_win.addstr(0, 0, prompt)
        return libcurses.getline(self.layout.cmdline_win)

    def update_display(self):
        """Update display."""

        if self.sound_alarm:
            self.sound_alarm = False
            if tf2mon.monitor.conlog.is_eof:  # don't do this when replaying logfile from start
                ...
                # playsound('/usr/share/sounds/sound-icons/prompt.wav')
                # playsound('/usr/share/sounds/sound-icons/cembalo-10.wav')
                # curses.flash()
                # curses.beep()

        self.refresh_kicks()
        self.refresh_spams()
        self.refresh_duels(Users.me)
        self.refresh_user(Users.me)
        # chatwin_blu and chatwin_red are rendered from gameplay/_playerchat
        self.scoreboard.refresh()
        self.show_status()
        self.grid.refresh()

    def refresh_chats(self):
        """Refresh chat panel(s)."""

        for win in [
            self.layout.chatwin_blu,
            self.layout.chatwin_red,
        ]:
            if win:
                win.erase()

        for chat in tf2mon.ChatsControl.value:
            self.show_chat(chat)

    def refresh_kicks(self):
        """Refresh kicks panel."""

        if self.layout.kicks_win:
            self._show_lines(
                "KICKS",
                reversed(tf2mon.KicksControl.msgs),
                self.layout.kicks_win,
            )

        if self.layout.user_win:
            self.refresh_user(Users.me)

    def refresh_spams(self):
        """Refresh spams panel."""

        if self.layout.spams_win:
            self._show_lines(
                "SPAMS",
                reversed(tf2mon.SpamsControl.msgs),
                self.layout.spams_win,
            )

        if self.layout.user_win:
            self.refresh_user(Users.me)

    def refresh_duels(self, user):
        """Refresh duels panel."""

        if self.layout.duels_win:
            self._show_lines("user", self._format_duels(user), self.layout.duels_win)

        if self.layout.user_win:
            self.refresh_user(Users.me)

    def refresh_user(self, user):
        """Refresh user panel."""

        panel = tf2mon.UserPanelControl
        kicks = tf2mon.KicksControl
        spams = tf2mon.SpamsControl

        if self.layout.user_win:
            if panel.value == panel.enum.KICKS or (
                panel.value == panel.enum.AUTO and kicks.msgs
            ):
                self._show_lines(
                    "KICKS",
                    reversed(kicks.msgs) if kicks.msgs else ["No Kicks"],
                    self.layout.user_win,
                )
            #
            elif panel.value == panel.enum.SPAMS or (
                panel.value == panel.enum.AUTO and spams.msgs
            ):
                self._show_lines(
                    "SPAMS",
                    reversed(spams.msgs) if spams.msgs else ["No Spams"],
                    self.layout.user_win,
                )
            #
            else:
                self._show_lines("user", self._format_duels(user), self.layout.user_win)

            self.layout.user_win.noutrefresh()

    def user_color(self, user, color):
        """Return `color` to display `user` in scoreboard."""

        if user.display_level:
            color = self.colormap[user.display_level]

        if user == Users.my.last_killer:
            color |= curses.A_BOLD | curses.A_ITALIC

        if user == Users.my.last_victim:
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
            win = self.layout.chatwin_red
        if not win:
            win = self.layout.chatwin_blu  # unassigned, or RED in shared window.
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

    def show_journal(self, level: str, line: str) -> None:
        """Display `line` in some pseudo "journal" window."""

        if (win := self.layout.chatwin_blu) is None:
            return

        if sum(win.getyx()):
            win.addch("\n")
        win.addstr(line, self.colormap[level])
        win.noutrefresh()

    def show_player_intel(self, player) -> None:
        """Display what we know about `player`."""

        level = player.display_level
        leader = f"{level}: {player.steamid}"

        # self.show_journal(
        #     "Player",
        #     f"{leader}: {player}",
        # )

        # self.show_journal(
        #     level,
        #     f"{leader}: {player.astuple()}",
        # )

        self.show_journal(
            level,
            f"{leader}: name: `{player.last_name}`",
        )

        for alias in [x for x in player.aliases if x != player.last_name]:
            self.show_journal(
                level,
                f"{leader}: alias: `{alias}`",
            )

        self.show_journal(
            level,
            # pylint: disable=protected-access
            f"{leader}: prev={player.s_prev_time} {player._s_prev_time}",
        )

        self.show_journal(
            level,
            f"{leader}: attrs={[x for x in player.getattrs() if x]}",
        )

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

        line = tf2mon.controller.get_status_line() + f" UID={Users.my.userid}"

        try:
            self.layout.status_win.addstr(
                0, 0, line, self.colormap["NOTIFY" if self.notify_operator else "STATUS"]
            )
            self.layout.status_win.clrtoeol()
        except curses.error:
            pass
        self.layout.status_win.noutrefresh()

    def _show_lines(self, level, lines, win):

        win.erase()

        with contextlib.suppress(curses.error):
            for line in lines:
                win.addstr(line + "\n", self.colormap[level])
        win.noutrefresh()
