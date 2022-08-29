"""Team Fortress 2 Console Monitor."""

from __future__ import annotations

import csv
import curses
import re
import threading
from pathlib import Path
from pprint import pformat

import libcurses
from loguru import logger

import tf2mon
from tf2mon.admin import Admin
from tf2mon.conlog import Conlog
from tf2mon.database import Database
from tf2mon.gameplay import Gameplay
from tf2mon.msgqueue import MsgQueueManager
from tf2mon.player import Player
from tf2mon.regex import Regex
from tf2mon.role import Role
from tf2mon.steamplayer import SteamPlayer
from tf2mon.steamweb import SteamWebAPI
from tf2mon.ui import UI
from tf2mon.user import Team, User
from tf2mon.users import Users


class Monitor:
    """Team Fortress 2 Console Monitor."""

    # pylint: disable=too-many-instance-attributes

    # Defer initializing these items until after parsing args.
    tf2_scripts_dir: Path
    path_static_script: Path
    path_dynamic_script: Path
    msgqueues: MsgQueueManager
    conlog: Conlog
    steam_web_api: SteamWebAPI
    roles: dict[str, list[Role]]
    sniper_role: Role
    unknown_role: Role
    role_by_weapon: dict[str, str]
    _re_racist: type[re.Pattern]
    users: Users
    me: User
    my: User
    chats: list
    admin: Admin
    gameplay: Gameplay
    regex_list: list
    ui: UI

    def _init(self) -> None:
        """Complete initialization; post CLI, options now available."""

        # Location of TF2 `exec` scripts.
        self.tf2_scripts_dir = Path(tf2mon.options.tf2_install_dir, "cfg", "user")
        if not self.tf2_scripts_dir.is_dir():
            logger.warning(f"Missing TF2 scripts dir `{self.tf2_scripts_dir}`")

        # Monitor aliases and key bindings.
        self.path_static_script = self.tf2_scripts_dir / "tf2mon.cfg"  # created once

        # "Send" to TF2 through `msgqueues`.
        self.path_dynamic_script = self.tf2_scripts_dir / "tf2mon-pull.cfg"  # created often
        self.msgqueues = MsgQueueManager(self.path_dynamic_script)

        # "Receive" from TF2 through `conlog`.
        # Wait for con_logfile to exist, then open it.
        self.conlog = Conlog(
            tf2mon.options.con_logfile,
            exclude_file=tf2mon.options.exclude_file,
            rewind=tf2mon.options.rewind,
            follow=tf2mon.options.follow,
            inject_cmds=tf2mon.options.inject_cmds,
            inject_file=tf2mon.options.inject_file,
        )

        #
        self.steam_web_api = SteamWebAPI(webapi_key=tf2mon.config.get("webapi_key"))

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

        self.chats = []
        # this application's admin console
        self.admin = Admin()
        if tf2mon.options.breakpoint is not None:
            self.admin.set_single_step_lineno(tf2mon.options.breakpoint)

        # admin command handlers
        self.regex_list = self.admin.regex_list

        # gameplay handlers
        self.gameplay = Gameplay()
        self.regex_list += self.gameplay.regex_list

        # function key handlers
        self.write_tf2_exec_script()
        self.regex_list += tf2mon.controls.get_regex_list()

    def run(self):
        """Run the Monitor."""

        libcurses.wrapper(self._run)

    def _run(self, win):

        self._init()
        tf2mon.ui = self.ui = UI(win)
        tf2mon.controls.start()
        self.reset_game()

        # no need for threads if exiting at end of conlog
        if not tf2mon.options.follow:
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

        self.users = Users()
        self.me = self.my = self.users[tf2mon.config.get("player_name")]
        self.me.assign_team(Team.BLU)
        self.my.display_level = "user"
        self.chats = []
        tf2mon.ui.refresh_chats()
        self.msgqueues.clear()

    def repl(self):
        """Read the console log file and play game."""

        Database(tf2mon.options.database, [Player, SteamPlayer])
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

        if self.conlog.is_eof or self.admin.is_single_stepping:
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
        for user in self.users.users_by_username.values():
            logger.success(pformat(user.__dict__))

    @property
    def toggling_enabled(self) -> bool:
        """Return True if toggling is enabled.

        Don't allow toggling when replaying a game (`--rewind`),
        unless `--toggles` is also given... or if single-stepping

        This is checked by keys that alter the behavior of gameplay;
        it is not checked by keys that only alter the display.
        """

        return self.conlog.is_eof or tf2mon.options.toggles or self.admin.is_single_stepping

    def write_tf2_exec_script(self):
        """Write tf2 exec script."""

        if self.tf2_scripts_dir.is_dir():
            logger.info(f"Writing `{self.path_static_script}`")
            script = tf2mon.controls.commands.as_tf2_exec_script(
                str(self.path_static_script.relative_to(self.tf2_scripts_dir.parent)),
                str(self.path_dynamic_script.relative_to(self.tf2_scripts_dir.parent)),
            )
            self.path_static_script.write_text(script, encoding="utf-8")
        else:
            logger.warning(f"Not writing `{self.path_static_script}`")
