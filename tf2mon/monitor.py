"""Team Fortress 2 Console Monitor."""

import csv
import curses
import re
import threading
from pathlib import Path
from pprint import pformat

import libcurses
from loguru import logger

import tf2mon.control
from tf2mon.admin import Admin
from tf2mon.command import Command
from tf2mon.conlog import Conlog
from tf2mon.database import Session
from tf2mon.gameplay import Gameplay
from tf2mon.msgqueue import MsgQueueManager
from tf2mon.regex import Regex
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

        self.options = cli.options
        self.config = cli.config
        self.controls = cli.controls
        self.commands = self.controls.commands

        # Location of TF2 `exec` scripts.
        self.tf2_scripts_dir = Path(self.options.tf2_install_dir, "cfg", "user")
        if not self.tf2_scripts_dir.is_dir():
            logger.warning(f"Missing TF2 scripts dir `{self.tf2_scripts_dir}`")

        # Monitor aliases and key bindings.
        self.path_static_script = self.tf2_scripts_dir / "tf2mon.cfg"  # created once

        # "Send" to TF2 through `msgqueues`.
        self.path_dynamic_script = self.tf2_scripts_dir / "tf2mon-pull.cfg"  # created often
        self.msgqueues = MsgQueueManager(self, self.path_dynamic_script)

        # "Receive" from TF2 through `conlog`.
        # Wait for con_logfile to exist, then open it.
        self.conlog = Conlog(
            self.options.con_logfile,
            exclude_file=self.options.exclude_file,
            rewind=self.options.rewind,
            follow=self.options.follow,
            inject_cmds=self.options.inject_cmds,
            inject_file=self.options.inject_file,
        )

        # this application's admin console
        self.admin = Admin(self)
        if self.options.breakpoint is not None:
            self.admin.set_single_step_lineno(self.options.breakpoint)

        #
        Session(self.options.database)
        self.steam_web_api = SteamWebAPI(webapi_key=self.config.get("webapi_key"))

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
        self._re_racist = (
            re.compile("|".join(lines), flags=re.IGNORECASE) if len(lines) > 0 else None
        )

        # users
        self.users = None

        # chats
        self.chats = []

        # message queues
        self.kicks = self.msgqueues.addq("kicks")
        self.spams = self.msgqueues.addq("spams")

        #
        self.spammer = Spammer(self)

        # admin command handlers
        self.regex_list = self.admin.regex_list

        # gameplay handlers
        self.gameplay = Gameplay(self)
        self.regex_list += self.gameplay.regex_list

        # function key handlers
        # self.add_commands()
        # self.regex_list += self.commands.get_regex_list()

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
        tf2mon.control.Control.monitor = self
        self.commands.register_curses_handlers()
        self.controls["SortOrderControl"].start(self.options.sort_order)
        self.controls["LogLocationControl"].start(self.options.log_location)
        self.controls["LogLevelControl"].start(self.options.verbose)
        self.controls["GridLayoutControl"].start(self.options.layout)

        self.reset_game()

        # no need for threads if exiting at end of conlog
        if not self.options.follow:
            self.repl()
            return

        # Read from conlog, write to display.
        thread = threading.Thread(name="GAME", target=self.repl, daemon=True)
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
        self.chats = []
        self.msgqueues.clear()

    def repl(self):
        """Read the console log file and play game."""

        self.conlog.open()

        while (line := self.conlog.readline()) is not None:
            if not line:
                continue

            regex = Regex.search_list(line, self.regex_list)
            if not regex:
                logger.log("ignore", self.conlog.last_line)
                continue

            self.admin.step(line)
            regex.handler(regex.re_match_obj)
            self.msgqueues.send()
            self.ui.update_display()

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
        return self._re_racist.search(text)

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

    def add_commands(self):
        """Init and return `CommandManager`."""

        # numpad
        self.commands.bind(self._cmd_pull(), "KP_UPARROW")
        self.commands.bind(self._cmd_clear_queues(), "KP_5")
        self.commands.bind(self._cmd_push(), "KP_DOWNARROW")
        self.commands.bind(self._cmd_spams_pop(), "KP_PGUP")
        self.commands.bind(self._cmd_spams_clear(), "KP_RIGHTARROW")
        self.commands.bind(self._cmd_spams_popleft(), "KP_PGDN")

        if self.tf2_scripts_dir.is_dir():
            logger.info(f"Writing `{self.path_static_script}`")
            script = self.commands.as_tf2_exec_script(
                str(self.path_static_script.relative_to(self.tf2_scripts_dir.parent)),
                str(self.path_dynamic_script.relative_to(self.tf2_scripts_dir.parent)),
            )
            self.path_static_script.write_text(script, encoding="utf-8")
        else:
            logger.warning(f"Not writing `{self.path_static_script}`")

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

    def _cmd_pull(self) -> Command:

        return Command(
            name="PULL",
            # handler=lambda m: logger.trace('pull'),
            action="tf2mon_pull",
        )

    def _cmd_clear_queues(self) -> Command:

        return Command(
            name="CLEAR-QUEUES",
            handler=lambda m: (
                self.kicks.clear(),
                self.ui.refresh_kicks(),
                self.spams.clear(),
                self.ui.refresh_spams(),
            ),
            action="tf2mon_clear_queues",
        )

    def _cmd_push(self) -> Command:

        return Command(
            name="PUSH",
            # handler=lambda m: logger.trace('push'),
            action="tf2mon_push",
        )

    def _cmd_spams_pop(self) -> Command:

        return Command(
            name="SPAMS-POP",
            handler=lambda m: (
                self.spams.pop(),
                self.ui.refresh_spams(),
            ),
            action="tf2mon_spams_pop",
        )

    def _cmd_spams_clear(self) -> Command:

        return Command(
            name="SPAMS-CLEAR",
            handler=lambda m: (
                self.spams.clear(),
                self.ui.refresh_spams(),
            ),
            action="tf2mon_spams_clear",
        )

    def _cmd_spams_popleft(self) -> Command:

        return Command(
            name="SPAMS-POPLEFT",
            handler=lambda m: (
                self.spams.popleft(),
                self.ui.refresh_spams(),
            ),
            action="tf2mon_spams_popleft",
        )
