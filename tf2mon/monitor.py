"""Team Fortress 2 Console Monitor."""

import csv
import curses
import re
import threading
from pathlib import Path
from pprint import pformat

import libcurses
from loguru import logger

from tf2mon.admin import Admin
from tf2mon.conlog import Conlog
from tf2mon.fkey import FKey, FKeyManager
from tf2mon.gameplay import Gameplay
from tf2mon.hacker import HackerAttr, HackerManager
from tf2mon.msgqueue import MsgQueueManager
from tf2mon.role import Role
from tf2mon.spammer import Spammer
from tf2mon.steamweb import SteamWebAPI
from tf2mon.ui import UI
from tf2mon.user import Team
from tf2mon.usermanager import UserManager


class Monitor:
    """Team Fortress 2 Console Monitor."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, cli) -> None:
        """Initialize monitor."""

        # pylint: disable=too-many-statements

        self.options = cli.options
        self.config = cli.config

        #
        self.steam_web_api = SteamWebAPI(
            dbpath=self.options.players,
            webapi_key=self.config.get("webapi_key"),
        )

        # send data to tf2 by writing to an `exec` script
        self.tf2_scripts_dir = Path(self.options.tf2_install_dir, "cfg", "user")
        if not self.tf2_scripts_dir.is_dir():
            logger.warning(f"Missing scripts at `{self.tf2_scripts_dir}`")
        self.msgqueues = MsgQueueManager(self, self.tf2_scripts_dir / "tf2-monitor-work.cfg")

        # receive data from tf2 by reading its console logfile
        self.conlog = Conlog(
            self.options.con_logfile,
            rewind=self.options.rewind,
            follow=self.options.follow,
            inject_cmds=self.options.inject_cmds,
            inject_file=self.options.inject_file,
        )

        # this application's admin console
        self.admin = Admin(self)

        #
        self.hackers = HackerManager(
            base=self.options.hackers_base,
            local=self.options.hackers_local,
        )

        #
        self.roles = Role.get_roles_by_name()
        self.sniper_role = self.roles["sniper"]
        self.unknown_role = self.roles["unknown"]

        #
        path = Path(__file__).parent / "data" / "weapons.csv"
        logger.info(f"Reading `{path}`")
        with open(path, encoding="utf-8") as _f:
            self.role_by_weapon = {weapon: self.roles[role] for role, weapon in csv.reader(_f)}

        #
        path = Path(__file__).parent / "data" / "racist.txt"
        logger.info(f"Reading `{path}`")
        lines = path.read_text(encoding="utf-8").splitlines()
        self._racist_re = (
            re.compile("|".join(lines), flags=re.IGNORECASE) if len(lines) > 0 else None
        )

        # users
        self.users = None

        # message queues
        self.kicks = self.msgqueues.addq("kicks")
        self.spams = self.msgqueues.addq("spams")

        #
        self.spammer = Spammer(self)

        # function keys
        self.fkeys = FKeyManager()
        self.fkeys.add(self._fkey_help("F1", curses.KEY_F1))
        self.fkeys.add(self._fkey_motd(None, curses.KEY_F13))
        self.fkeys.add(self._fkey_debug_flag("F2", curses.KEY_F2))
        self.fkeys.add(self._fkey_log_level("F14", curses.KEY_F14))
        self.fkeys.add(self._fkey_taunt_flag("F3", curses.KEY_F3))
        self.fkeys.add(self._fkey_show_kd("F4", curses.KEY_F4))
        self.fkeys.add(self._fkey_user_panel("F5", curses.KEY_F5))
        self.fkeys.add(self._fkey_join_other_team("F6", curses.KEY_F6))
        self.fkeys.add(self._fkey_sort_order("F7", curses.KEY_F7))
        self.fkeys.add(self._fkey_log_location("F8", curses.KEY_F8))
        self.fkeys.add(self._fkey_reset_padding("F20", curses.KEY_F20))
        self.fkeys.add(self._fkey_grid_layout("F9", curses.KEY_F9))
        self.fkeys.add(self._fkey_show_debug("KP_INS", curses.KEY_IC))
        self.fkeys.add(self._fkey_single_step("KP_DEL", curses.KEY_DC))
        self.fkeys.add(self._fkey_kick_last_cheater("[", None))
        self.fkeys.add(self._fkey_kick_last_racist("]", None))
        self.fkeys.add(self._fkey_kick_last_suspect("\\", None))
        # numpad
        self.fkeys.add(self._fkey_kicks_pop("KP_HOME", curses.KEY_HOME))
        self.fkeys.add(self._fkey_kicks_clear("KP_LEFTARROW", curses.KEY_LEFT))
        self.fkeys.add(self._fkey_kicks_popleft("KP_END", curses.KEY_END))
        self.fkeys.add(self._fkey_pull("KP_UPARROW", curses.KEY_UP))
        self.fkeys.add(self._fkey_clear_queues("KP_5", curses.KEY_B2))
        self.fkeys.add(self._fkey_push("KP_DOWNARROW", curses.KEY_DOWN))
        self.fkeys.add(self._fkey_spams_pop("KP_PGUP", curses.KEY_PPAGE))
        self.fkeys.add(self._fkey_spams_clear("KP_RIGHTARROW", curses.KEY_RIGHT))
        self.fkeys.add(self._fkey_spams_popleft("KP_PGDN", curses.KEY_NPAGE))
        #
        if self.tf2_scripts_dir.is_dir():
            self.fkeys.create_tf2_exec_script(self.tf2_scripts_dir / "tf2-monitor-fkeys.cfg")

        # admin command handlers
        self.regex_list = self.admin.regex_list

        # gameplay handlers
        self.gameplay = Gameplay(self)
        self.regex_list += self.gameplay.regex_list

        # function key handlers
        self.regex_list += self.fkeys.get_regex_list()

        #
        self.me = self.my = None
        self.ui = None
        self.reset_game()

    def run(self):
        """Run the Monitor."""
        libcurses.wrapper(self._run)

    def _run(self, win):
        # Build user-interface
        self.ui = UI(self, win)
        self.reset_game()

        # no need for threads if exiting at end of conlog
        if not self.options.follow:
            self.gameplay.repl()
            return

        # Read from conlog, write to display.
        thread = threading.Thread(name="GAME", target=self.gameplay.repl, daemon=True)
        thread.start()

        # main thread reads from keyboard/mouse, and writes to display
        # threading.current_thread().name = "MAIN"
        self.admin.repl()

    def reset_game(self):
        """Start new game."""

        logger.success("RESET GAME")

        self.users = UserManager(self)
        self.me = self.my = self.users.find_username(self.config["player_name"])
        self.me.assign_team(Team.BLU)
        self.my.display_level = "user"

        self.msgqueues.clear()
        if self.ui:
            self.ui.clear_chats()

    def breakpoint(self):
        """Drop into python debugger."""

        if self.conlog.is_eof:  # don't do this when replaying logfile from start
            curses.reset_shell_mode()
            breakpoint()  # pylint: disable=forgotten-debug-statement
            curses.reset_prog_mode()

    def kick_my_last_killer(self, attr):
        """Kick the last user who killed the operator."""

        if self.my.last_killer:
            self.my.last_killer.kick(attr)
        else:
            logger.warning("no last killer")

    def is_racist_text(self, text):
        """Return True if this user appears to be racist."""
        return self._racist_re.search(text)

    def dump(self) -> None:
        """Dump stuff."""

        # logger.success(pformat(self.__dict__))
        logger.success(pformat(self.users.__dict__))
        # pylint: disable=protected-access
        for user in self.users._users_by_username.values():
            logger.success(pformat(user.__dict__))

    @property
    def toggling_enabled(self) -> bool:
        """Return True if toggling is enabled.

        Don't allow toggling when replaying a game (`--rewind`),
        unless `--toggles` is also given... or if single-stepping

        This is checked by keys that alter the behavior of gameplay;
        it is not checked by keys that only alter the display.
        """

        return self.conlog.is_eof or self.options.toggles or self.admin.is_single_stepping

    @staticmethod
    def _on_off(key, value):
        return key.upper() if value else key

    def _fkey_help(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="HELP",
            game_key=game_key,
            curses_key=curses_key,
            status=lambda: "HELP",
            handler=lambda m: self.ui.show_help(),
        )

    def _fkey_motd(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="MOTD",
            game_key=game_key,
            curses_key=curses_key,
            handler=lambda m: self.ui.show_motd(),
        )

    def _fkey_debug_flag(self, game_key: str, curses_key: int) -> FKey:
        def _action() -> None:
            if self.toggling_enabled:
                _ = self.ui.debug_flag.toggle
                self.ui.show_status()

        return FKey(
            cmd="TOGGLE-DEBUG",
            game_key=game_key,
            curses_key=curses_key,
            status=lambda: self._on_off("debug", self.ui.debug_flag.value),
            handler=lambda m: _action(),
        )

    def _fkey_taunt_flag(self, game_key: str, curses_key: int) -> FKey:
        def _action() -> None:
            if self.toggling_enabled:
                _ = self.ui.taunt_flag.toggle
                self.ui.show_status()

        return FKey(
            cmd="TOGGLE-TAUNT",
            game_key=game_key,
            curses_key=curses_key,
            status=lambda: self._on_off("taunt", self.ui.taunt_flag.value),
            handler=lambda m: _action(),
        )

    def _fkey_show_kd(self, game_key: str, curses_key: int) -> FKey:
        def _action() -> None:
            if self.toggling_enabled:
                _ = self.ui.show_kd.toggle
                self.ui.show_status()

        return FKey(
            cmd="TOGGLE-KD",
            game_key=game_key,
            curses_key=curses_key,
            status=lambda: self._on_off("kd", self.ui.show_kd.value),
            handler=lambda m: _action(),
        )

    def _fkey_user_panel(self, game_key: str, curses_key: int) -> FKey:
        def _action() -> None:
            _ = self.ui.user_panel.toggle
            self.ui.update_display()

        return FKey(
            cmd="TOGGLE-USER-PANEL",
            game_key=game_key,
            curses_key=curses_key,
            status=lambda: self.ui.user_panel.value.name,
            handler=lambda m: _action(),
        )

    def _fkey_join_other_team(self, game_key: str, curses_key: int) -> FKey:
        def _action() -> None:
            if self.toggling_enabled:
                self.me.assign_team(self.my.opposing_team)
                self.ui.update_display()

        return FKey(
            cmd="SWITCH-MY-TEAM",
            game_key=game_key,
            curses_key=curses_key,
            status=lambda: self.my.team.name if self.my.team else "blu",
            handler=lambda m: _action(),
        )

    def _fkey_sort_order(self, game_key: str, curses_key: int) -> FKey:
        def _action() -> None:
            self.ui.set_sort_order(self.ui.sort_order.toggle)
            self.ui.update_display()

        return FKey(
            cmd="TOGGLE-SORT",
            game_key=game_key,
            curses_key=curses_key,
            status=lambda: self.ui.sort_order.value.name,
            handler=lambda m: _action(),
        )

    def _fkey_log_level(self, game_key: str, curses_key: int) -> FKey:
        def _action() -> None:
            self.ui.cycle_log_level()
            self.ui.show_status()

        return FKey(
            cmd="TOGGLE-LOG-LEVEL",
            game_key=game_key,
            curses_key=curses_key,
            status=lambda: self.ui.log_level.value.name,
            handler=lambda m: _action(),
        )

    def _fkey_log_location(self, game_key: str, curses_key: int) -> FKey:
        def _action() -> None:
            self.ui.cycle_log_location()
            self.ui.show_status()

        return FKey(
            cmd="TOGGLE-LOG-LOCATION",
            game_key=game_key,
            curses_key=curses_key,
            status=lambda: self.ui.log_location.value.name,
            handler=lambda m: _action(),
        )

    def _fkey_reset_padding(self, game_key: str, curses_key: int) -> FKey:
        def _action() -> None:
            self.ui.logsink.reset_padding()
            logger.info("padding reset")

        return FKey(
            game_key=game_key,
            curses_key=curses_key,
            handler=lambda m: _action(),
            # handler=lambda m: self.ui.logsink.reset_padding(),
        )

    def _fkey_grid_layout(self, game_key: str, curses_key: int) -> FKey:
        def _action() -> None:
            self.ui.cycle_grid_layout()

        return FKey(
            cmd="TOGGLE-LAYOUT",
            game_key=game_key,
            curses_key=curses_key,
            status=lambda: self.ui.grid_layout.value.name,
            handler=lambda m: _action(),
        )

    def _fkey_single_step(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="SINGLE-STEP",
            game_key=game_key,
            curses_key=curses_key,
            handler=lambda m: self.admin.start_single_stepping(),
        )

    def _fkey_show_debug(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="SHOW-DEBUG",
            game_key=game_key,
            curses_key=curses_key,
            handler=lambda m: self.ui.show_debug(),
        )

    def _fkey_kick_last_cheater(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="KICK-LAST-CHEATER",
            game_key=game_key,
            curses_key=curses_key,
            status=lambda: HackerAttr.CHEATER.name,
            handler=lambda m: self.kick_my_last_killer(HackerAttr.CHEATER),
        )

    def _fkey_kick_last_racist(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="KICK-LAST-RACIST",
            game_key=game_key,
            curses_key=curses_key,
            status=lambda: HackerAttr.RACIST.name,
            handler=lambda m: self.kick_my_last_killer(HackerAttr.RACIST),
        )

    def _fkey_kick_last_suspect(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="KICK-LAST-SUSPECT",
            game_key=game_key,
            curses_key=curses_key,
            status=lambda: HackerAttr.SUSPECT.name,
            handler=lambda m: self.kick_my_last_killer(HackerAttr.SUSPECT),
        )

    # --------------------------------------------------------------------------
    # Numpad
    #                      kicks     admin     spams
    #                        |         |         |
    #                        v         v         v
    #                   +-----------------------------+
    #        last/      |         |         |         |
    #        latest --> |   pop   |  pull   |   pop   |
    #                   |         |         |         |
    #                   |---------+---------+---------|
    #                   |         |         |         |
    #                   |  clear  |  clear  |  clear  |
    #                   |         |  both   |         |
    #                   |---------+---------+---------|
    #        first/     |         |         |         |
    #        oldest --> | popleft |  push   | popleft |
    #                   |         |         |         |
    #                   +-----------------------------+

    def _fkey_kicks_pop(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="KICKS-POP",
            game_key=game_key,
            curses_key=curses_key,
            handler=lambda m: (
                self.kicks.pop(),
                self.ui.refresh_kicks(),
            ),
            action="tf2mon_kicks_pop",
        )

    def _fkey_kicks_clear(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="KICKS-CLEAR",
            game_key=game_key,
            curses_key=curses_key,
            handler=lambda m: (
                self.kicks.clear(),
                self.ui.refresh_kicks(),
            ),
            action="tf2mon_kicks_clear",
        )

    def _fkey_kicks_popleft(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="KICKS-POPLEFT",
            game_key=game_key,
            curses_key=curses_key,
            handler=lambda m: (
                self.kicks.popleft(),
                self.ui.refresh_kicks(),
            ),
            action="tf2mon_kicks_popleft",
        )

    def _fkey_pull(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="PULL",
            game_key=game_key,
            curses_key=curses_key,
            # handler=lambda m: logger.trace('pull'),
            action="tf2mon_pull",
        )

    def _fkey_clear_queues(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="CLEAR-QUEUES",
            game_key=game_key,
            curses_key=curses_key,
            handler=lambda m: (
                self.kicks.clear(),
                self.ui.refresh_kicks(),
                self.spams.clear(),
                self.ui.refresh_spams(),
            ),
            action="tf2mon_clear_queues",
        )

    def _fkey_push(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="PUSH",
            game_key=game_key,
            curses_key=curses_key,
            # handler=lambda m: logger.trace('push'),
            action="tf2mon_push",
        )

    def _fkey_spams_pop(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="SPAMS-POP",
            game_key=game_key,
            curses_key=curses_key,
            handler=lambda m: (
                self.spams.pop(),
                self.ui.refresh_spams(),
            ),
            action="tf2mon_spams_pop",
        )

    def _fkey_spams_clear(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="SPAMS-CLEAR",
            game_key=game_key,
            curses_key=curses_key,
            handler=lambda m: (
                self.spams.clear(),
                self.ui.refresh_spams(),
            ),
            action="tf2mon_spams_clear",
        )

    def _fkey_spams_popleft(self, game_key: str, curses_key: int) -> FKey:

        return FKey(
            cmd="SPAMS-POPLEFT",
            game_key=game_key,
            curses_key=curses_key,
            handler=lambda m: (
                self.spams.popleft(),
                self.ui.refresh_spams(),
            ),
            action="tf2mon_spams_popleft",
        )
