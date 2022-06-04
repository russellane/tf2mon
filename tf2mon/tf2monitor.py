"""Team Fortress 2 Console Monitor."""

import argparse
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
from tf2mon.fkey import FKeyManager
from tf2mon.gameplay import Gameplay
from tf2mon.hacker import HackerManager
from tf2mon.msgqueue import MsgQueueManager
from tf2mon.role import Role
from tf2mon.spammer import Spammer
from tf2mon.steamweb import SteamWebAPI
from tf2mon.ui import UI
from tf2mon.user import Team
from tf2mon.usermanager import UserManager


class TF2Monitor:
    """Team Fortress 2 Console Monitor."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, options: argparse.Namespace, config: {}) -> None:
        """Initialize monitor."""

        self.options = options
        self.config = config

        #
        self.steam_web_api = SteamWebAPI(
            dbpath=self.options.players,
            webapi_key=self.config["webapi_key"],
        )

        # send data to tf2 by writing to an `exec` script
        self.tf2_cfg_dir = Path(self.options.tf2_install_dir, "cfg")
        self.tf2_scripts_dir = Path(self.tf2_cfg_dir, "user")
        self.worker_path = Path(self.tf2_scripts_dir, "tf2-monitor-work.cfg")
        self.msgqueues = MsgQueueManager(self, self.worker_path)

        # prepare to receive data from tf2 by reading its console logfile
        self.conlog = Conlog(self)

        # inject any commands from the command line into the conlog
        self.conlog.inject_cmd_list(self.options.inject_cmds)

        # inject any commands from a file into the conlog
        if self.options.inject_file:
            logger.info(f"Reading `{self.options.inject_file}`")
            with open(self.options.inject_file, encoding="utf-8") as file:
                self.conlog.inject_cmd_list(file)

        # this application's admin console
        self.admin = Admin(self)

        # other options that inject commands...
        if self.options.breakpoint is not None:
            self.admin.set_single_step_lineno(self.options.breakpoint)

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
        self.fkeys = FKeyManager(self)
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

    @property
    def appname(self) -> str:
        """Application name."""
        return self.config["app-name"]

    @property
    def cmd_prefix(self) -> str:
        """Return command prefix string."""
        # We bind TF2 function keys to a) perform an action [optional], and
        # b) `echo` a command message to the con_logfile to inform us the
        # function key was pressed. Tag all command messages to avoid
        # colliding with lines generated by TF2.
        return self.appname + "-"

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
        thread = threading.Thread(name="game", target=self.gameplay.repl, daemon=True)
        thread.start()

        # main thread reads from keyboard/mouse, and writes to display
        threading.current_thread().name = "main"
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
