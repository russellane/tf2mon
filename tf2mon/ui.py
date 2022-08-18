"""User Interface."""

import contextlib
import curses
import os
import sys
import textwrap

import libcurses
from loguru import logger

import tf2mon
from tf2mon.scoreboard import Scoreboard
from tf2mon.user import Team, UserState

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

        # `register_builder` 1) calls `build_grid` and 2) configures
        # `KEY_RESIZE` to call it again each time that event occurs.
        self.grid.register_builder(self.build_grid)

        #
        self.logsink = libcurses.Sink(self.logger_win)
        #

        self.colormap = libcurses.get_colormap()
        #
        self.scoreboard = Scoreboard(
            self.scorewin_blu,
            self.colormap[Team.BLU.name],
            self.scorewin_red,
            self.colormap[Team.RED.name],
        )

    def build_grid(self):
        """Add boxes to grid.

        Called at init, on KEY_RESIZE events, and when layout changes.
        """

        klass = tf2mon.monitor.controls["GridLayoutControl"].value
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

        for win in [
            self.chatwin_blu,
            self.chatwin_red,
            self.logger_win,
        ]:
            if win:
                win.scrollok(True)

        for win in [
            self.scorewin_blu,
            self.scorewin_red,
            self.user_win,
            self.kicks_win,
            self.spams_win,
            self.duels_win,
            self.status_win,
        ]:
            if win:
                win.scrollok(False)

        if self.cmdline_win:
            self.cmdline_win.scrollok(True)
            self.cmdline_win.keypad(True)

        self.refresh_chats()
        self.grid.redraw()

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
            if tf2mon.monitor.conlog.is_eof:  # don't do this when replaying logfile from start
                ...
                # playsound('/usr/share/sounds/sound-icons/prompt.wav')
                # playsound('/usr/share/sounds/sound-icons/cembalo-10.wav')
                # curses.flash()
                # curses.beep()

        self.refresh_kicks()
        self.refresh_spams()
        self.refresh_duels(tf2mon.monitor.me)
        self.refresh_user(tf2mon.monitor.me)
        # chatwin_blu and chatwin_red are rendered from gameplay/_playerchat
        self.scoreboard.show_scores(
            team1=list(tf2mon.monitor.users.active_team_users(Team.BLU)),
            team2=list(tf2mon.monitor.users.active_team_users(Team.RED)),
        )
        self.show_status()
        self.grid.refresh()

    def refresh_chats(self):
        """Refresh chat panel(s)."""

        for win in [
            self.chatwin_blu,
            self.chatwin_red,
        ]:
            if win:
                win.erase()

        for chat in tf2mon.monitor.chats:
            self.show_chat(chat)

    def refresh_kicks(self):
        """Refresh kicks panel."""

        if self.kicks_win:
            # ic(self.kicks_win.getbegyx())
            # ic(self.kicks_win.getmaxyx())
            self._show_lines("KICKS", reversed(tf2mon.monitor.kicks.msgs), self.kicks_win)

        # if self.user_win:
        #     self.refresh_user(tf2mon.monitor.me)

    def refresh_spams(self):
        """Refresh spams panel."""

        if self.spams_win:
            self._show_lines("SPAMS", reversed(tf2mon.monitor.spams.msgs), self.spams_win)

        if self.user_win:
            self.refresh_user(tf2mon.monitor.me)

    def refresh_duels(self, user):
        """Refresh duels panel."""

        if self.duels_win:
            self._show_lines("user", self._format_duels(user), self.duels_win)

        if self.user_win:
            self.refresh_user(tf2mon.monitor.me)

    def refresh_user(self, user):
        """Refresh user panel."""

        ctrl = tf2mon.monitor.controls["UserPanelControl"]

        if self.user_win:
            if ctrl.value == ctrl.enum.KICKS or (
                ctrl.value == ctrl.enum.AUTO and tf2mon.monitor.kicks.msgs
            ):
                self._show_lines(
                    "KICKS",
                    reversed(tf2mon.monitor.kicks.msgs)
                    if tf2mon.monitor.kicks.msgs
                    else ["No Kicks"],
                    self.user_win,
                )
            #
            elif ctrl.value == ctrl.enum.SPAMS or (
                ctrl.value == ctrl.enum.AUTO and tf2mon.monitor.spams.msgs
            ):
                self._show_lines(
                    "SPAMS",
                    reversed(tf2mon.monitor.spams.msgs)
                    if tf2mon.monitor.spams.msgs
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

        if user == tf2mon.monitor.my.last_killer:
            color |= curses.A_BOLD | curses.A_ITALIC

        if user == tf2mon.monitor.my.last_victim:
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

    def show_journal(self, level: str, line: str) -> None:
        """Display `line` in some pseudo "journal" window."""

        if (win := self.chatwin_blu) is None:
            return

        if sum(win.getyx()):
            win.addch("\n")
        win.addstr(line, self.colormap[level])
        win.noutrefresh()

    def show_player_intel(self, player) -> None:
        """Display what we know about `player`."""

        level = player.display_level
        leader = f"{level}: {player.steamid}"

        # tf2mon.monitor.ui.show_journal(
        #     "Player",
        #     f"{leader}: {player}",
        # )

        # tf2mon.monitor.ui.show_journal(
        #     level,
        #     f"{leader}: {player.astuple()}",
        # )

        tf2mon.monitor.ui.show_journal(
            level,
            f"{leader}: name: `{player.last_name}`",
        )

        for alias in [x for x in player.aliases if x != player.last_name]:
            tf2mon.monitor.ui.show_journal(
                level,
                f"{leader}: alias: `{alias}`",
            )

        tf2mon.monitor.ui.show_journal(
            level,
            # pylint: disable=protected-access
            f"{leader}: prev={player.s_prev_time} {player._s_prev_time}",
        )

        tf2mon.monitor.ui.show_journal(
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

        line = tf2mon.monitor.controls.get_status_line() + f" UID={tf2mon.monitor.my.userid}"

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

        for line in tf2mon.monitor.controls.fkey_help().splitlines():
            self.show_journal("help", line)

    def show_motd(self):
        """Show message of the day."""

        motd = tf2mon.monitor.tf2_scripts_dir.parent / "motd.txt"
        logger.log("help", f" {motd} ".center(80, "-"))

        with open(motd, encoding="utf-8") as file:
            for line in file:
                logger.log("help", line.strip())

    def show_debug(self):
        """Debug grid."""

        logger.debug(self.grid)
        for box in self.grid.boxes:
            logger.debug(self.grid.winyx(box))
