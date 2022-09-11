"""Team Fortress 2 Console Monitor."""

from __future__ import annotations

import curses
import threading
from pathlib import Path

import libcurses
from loguru import logger

import tf2mon
import tf2mon.monitor as _Monitor
from tf2mon.admin import Admin
from tf2mon.conlog import Conlog
from tf2mon.database import Database
from tf2mon.gameplay import Gameplay
from tf2mon.player import Player
from tf2mon.racist import load_racist_data
from tf2mon.regex import Regex
from tf2mon.role import load_weapons_data
from tf2mon.steamplayer import SteamPlayer
from tf2mon.ui import UI


class Monitor:
    """Team Fortress 2 Console Monitor."""

    # Defer initializing until after parsing args.
    path_static_script: Path
    path_dynamic_script: Path
    regex_list: list
    ui: UI

    def run(self):
        """Run the Monitor."""

        libcurses.wrapper(self._run)

    def _run(self, win: curses.window) -> None:
        """Complete initialization; post CLI, options now available."""

        # Location of TF2 `exec` scripts.
        _Monitor.tf2_scripts_dir = Path(tf2mon.options.tf2_install_dir, "cfg", "user")
        if not _Monitor.tf2_scripts_dir.is_dir():
            logger.warning(f"Missing TF2 scripts dir `{_Monitor.tf2_scripts_dir}`")

        # Monitor aliases and key bindings.
        self.path_static_script = _Monitor.tf2_scripts_dir / "tf2mon.cfg"  # written once

        # "Send" to TF2 through `msgqueues`.
        self.path_dynamic_script = _Monitor.tf2_scripts_dir / "tf2mon-pull.cfg"  # written often

        tf2mon.MsgQueuesControl.open(self.path_dynamic_script)
        tf2mon.MsgQueuesControl.append(tf2mon.KicksControl)
        tf2mon.MsgQueuesControl.append(tf2mon.SpamsControl)

        # "Receive" from TF2 through `conlog`.
        # Wait for con_logfile to exist, then open it.
        _Monitor.conlog = Conlog(tf2mon.options)

        #
        load_weapons_data(Path(__file__).parent / "data" / "weapons.csv")
        load_racist_data(Path(__file__).parent / "data" / "racist.txt")

        # this application's admin console
        _Monitor.admin = Admin()
        if tf2mon.options.breakpoint is not None:
            _Monitor.admin.set_single_step_lineno(tf2mon.options.breakpoint)

        # admin command handlers
        self.regex_list = _Monitor.admin.regex_list

        # gameplay handlers
        self.regex_list += Gameplay().regex_list

        # function key handlers
        self.write_tf2_exec_script()
        self.regex_list += tf2mon.controls.get_regex_list()

        #
        _Monitor.ui = UI(win)
        _Monitor.options = tf2mon.options
        tf2mon.controls.start()
        _Monitor.users.me = _Monitor.users.my = _Monitor.users[tf2mon.config.get("player_name")]
        _Monitor.reset_game()

        # no need for threads if exiting at end of conlog
        if not tf2mon.options.follow:
            self.repl()
            return

        # Read from conlog, write to display.
        thread = threading.Thread(name="GAME", target=self.repl, daemon=True)
        thread.start()

        # main thread reads from keyboard/mouse, and writes to display
        # threading.current_thread().name = "MAIN"
        _Monitor.admin.repl()

    def repl(self):
        """Read the console log file and play game."""

        Database(tf2mon.options.database, [Player, SteamPlayer])
        _Monitor.conlog.open()

        while (line := _Monitor.conlog.readline()) is not None:
            if not line:
                continue

            regex = Regex.search_list(line, self.regex_list)
            if not regex:
                logger.log("ignore", _Monitor.conlog.last_line)
                continue

            _Monitor.admin.step(line)
            regex.handler(regex.re_match_obj)
            tf2mon.MsgQueuesControl.send()
            _Monitor.ui.update_display()

    def write_tf2_exec_script(self):
        """Write tf2 exec script."""

        if _Monitor.tf2_scripts_dir.is_dir():
            logger.info(f"Writing `{self.path_static_script}`")
            script = tf2mon.controls.commands.as_tf2_exec_script(
                str(self.path_static_script.relative_to(_Monitor.tf2_scripts_dir.parent)),
                str(self.path_dynamic_script.relative_to(_Monitor.tf2_scripts_dir.parent)),
            )
            self.path_static_script.write_text(script, encoding="utf-8")
        else:
            logger.warning(f"Not writing `{self.path_static_script}`")
