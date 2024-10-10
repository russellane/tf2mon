"""User Interface."""

import contextlib
import curses
import os
import sys

import libcurses
from libcurses.bw import BorderedWindow
from loguru import logger

import tf2mon
from tf2mon.baselayout import BaseLayout
from tf2mon.chat import Chat
from tf2mon.player import Player
from tf2mon.scoreboard import Scoreboard
from tf2mon.user import Team, User

# from playsound import playsound


class UI:
    """User Interface."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, win: curses.window):
        """Initialize User Interface."""

        self.notify_operator = False
        self.sound_alarm = False

        # create empty grid
        self.grid = libcurses.Grid(win)

        self.scoreboard: Scoreboard
        self.logsink: libcurses.LogSink
        # self.colormap: dict[str, int]
        # self.layout: BaseLayout | None = None  # set by `build_grid`.
        self.layout: BaseLayout  # set by `build_grid`.

        # `register_builder` 1) calls `build_grid` and 2) configures
        # `KEY_RESIZE` to call it again each time that event occurs.
        self.grid.register_builder(self.build_grid)
        # assert self.layout

        # begin logging to curses window, too.
        self.logsink = libcurses.LogSink(self.layout.logger_win)

        # map of `loguru-level-name` to `curses-color/attr`.
        self.colormap = libcurses.get_colormap()

        #
        self.scoreboard = Scoreboard(
            self.layout.scorewin_blu,
            self.colormap[Team.BLU.name],
            self.layout.scorewin_red,
            self.colormap[Team.RED.name],
        )

        self.popup_win: BorderedWindow | None = None

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

        if (
            tf2mon.ui is not None
            and self.layout.chatwin_blu is not None
            and self.layout.chatwin_red is not None
        ):
            tf2mon.ChatsControl.refresh()
        self.grid.redraw()

    def getline(self, prompt: str | None = None) -> str | None:
        """Read and return next line from keyboard."""

        self.layout.cmdline_win.erase()
        if prompt:
            self.layout.cmdline_win.addstr(0, 0, prompt)
        return libcurses.getline(self.layout.cmdline_win)

    def update_display(self) -> None:
        """Update display."""

        if self.sound_alarm:
            self.sound_alarm = False
            if (
                tf2mon.conlog and tf2mon.conlog.is_eof
            ):  # don't do this when replaying logfile from start
                ...
                # playsound('/usr/share/sounds/sound-icons/prompt.wav')
                # playsound('/usr/share/sounds/sound-icons/cembalo-10.wav')
                # curses.flash()
                # curses.beep()

        self.refresh_kicks()
        self.refresh_spams()
        self.refresh_duels(tf2mon.users.me)
        self.refresh_user(tf2mon.users.me)
        # chatwin_blu and chatwin_red are rendered from gameplay/_playerchat
        self.scoreboard.refresh()
        self.show_status()

        if self.popup_win:
            self.popup_win.refresh()

    def refresh_kicks(self) -> None:
        """Refresh kicks panel."""

        if self.layout.kicks_win:
            self._show_lines(
                "KICKS",
                list(reversed(tf2mon.KicksControl.msgs)),
                self.layout.kicks_win,
            )

        if self.layout.user_win:
            self.refresh_user(tf2mon.users.me)

    def refresh_spams(self) -> None:
        """Refresh spams panel."""

        if self.layout.spams_win:
            self._show_lines(
                "SPAMS",
                list(reversed(tf2mon.SpamsControl.msgs)),
                self.layout.spams_win,
            )

        if self.layout.user_win:
            self.refresh_user(tf2mon.users.me)

    def refresh_duels(self, user: User) -> None:
        """Refresh duels panel."""

        if self.layout.duels_win:
            self._show_lines("user", self._format_duels(user), self.layout.duels_win)

        if self.layout.user_win:
            self.refresh_user(tf2mon.users.me)

    def refresh_user(self, user: User) -> None:
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
                    list(reversed(kicks.msgs)) if kicks.msgs else ["No Kicks"],
                    self.layout.user_win,
                )
            #
            elif panel.value == panel.enum.SPAMS or (
                panel.value == panel.enum.AUTO and spams.msgs
            ):
                self._show_lines(
                    "SPAMS",
                    list(reversed(spams.msgs)) if spams.msgs else ["No Spams"],
                    self.layout.user_win,
                )
            #
            else:
                self._show_lines("user", self._format_duels(user), self.layout.user_win)

            self.layout.user_win.noutrefresh()

    def user_color(self, user: User, color: int) -> int:
        """Return `color` to display `user` in scoreboard."""

        if user.display_level:
            color = self.colormap[user.display_level]

        if user == tf2mon.users.my.last_killer:
            color |= curses.A_BOLD | curses.A_ITALIC

        if user == tf2mon.users.my.last_victim:
            color |= curses.A_BOLD

        if user.selected:
            color |= curses.A_REVERSE

        if not user.team:
            color |= curses.A_UNDERLINE

        if user.cloner:
            color |= curses.A_ITALIC

        return color

    def show_chat(self, chat: Chat) -> None:
        """Display (append) `chat` in appropriate team window."""

        win = None
        if chat.user.team == Team.RED:
            win = self.layout.chatwin_red
        if not win:
            win = self.layout.chatwin_blu  # unassigned, or RED in shared window.
        if not win:
            return  # not showing chats

        user = chat.user
        color = self.colormap[user.team.name if user.team else "user"]
        if chat.teamflag:
            color |= curses.A_UNDERLINE
        user_color = self.user_color(user, color)

        leader = f"{chat.s_timestamp}: {chat.user.username:20.20}: "
        if sum(win.getyx()):
            win.addch("\n")
        win.addstr(leader + chat.msg, user_color)

        if tf2mon.ShowKillsControl.value and chat.msg != "/rtd":
            # self._show_last_duels(win, leader, user, user_color)
            indent = " " * 15
            for line in chat.user.format_user_stats():
                win.addstr(f"\n{leader}{indent}{line}")

        win.noutrefresh()

    def show_journal(self, level: str, line: str) -> None:
        """Display `line` in some pseudo "journal" window."""

        assert self.layout
        if (win := self.layout.chatwin_blu) is None:
            return

        if sum(win.getyx()):
            win.addch("\n")
        win.addstr(line, self.colormap[level])
        win.noutrefresh()

    def popup(self, level: str, text: str) -> None:
        """Display `text` in a popup window."""

        self.popup_win = BorderedWindow(
            self.grid.nlines - 10,
            80,
            self.grid.begin_y + 5,
            self.grid.begin_x + 20,
        )
        # self.popup_win.box()
        # self.popup_win.scrollok(True)
        self.popup_win.w.addstr(text, self.colormap[level])
        self.popup_win.refresh()

    def show_player_intel(self, player: Player) -> None:
        """Display what we know about `player`."""

        level = player.display_level
        leader = f"{level}: {player.steamid}"

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

    def _format_duels(self, user: User) -> list[str]:

        lines: list[str] = []
        indent = " " * 12  # 12=len("99 and 99 vs")

        lines.append("Duels:")
        for opponent in [x for x in user.opponents.values() if x.is_active]:
            lines.append(f"{user.duel_as_str(opponent, True)} vs {opponent.moniker}")

            if opponent.key in user.nkills_by_opponent_by_weapon:
                for weapon, count in user.nkills_by_opponent_by_weapon[opponent.key].items():
                    lines.append(f"{indent} K {count:2} {weapon}")

            if user.key in opponent.nkills_by_opponent_by_weapon:
                for weapon, count in opponent.nkills_by_opponent_by_weapon[user.key].items():
                    lines.append(f"{indent} D {count:2} {weapon}")

        return lines

    def show_status(self) -> None:
        """Update status line."""

        line = tf2mon.controller.get_status_line() + f" UID={tf2mon.users.my.userid}"

        try:
            self.layout.status_win.addstr(
                0, 0, line, self.colormap["NOTIFY" if self.notify_operator else "STATUS"]
            )
            self.layout.status_win.clrtoeol()
        except curses.error:
            pass
        self.layout.status_win.noutrefresh()

    def _show_lines(self, level: str, lines: list[str], win: curses.window) -> None:

        win.erase()

        with contextlib.suppress(curses.error):
            for line in lines:
                win.addstr(line + "\n", self.colormap[level])
        win.noutrefresh()
