"""Team Fortress 2 Console Monitor."""

import curses
import re
import threading
from pathlib import Path

import libcurses
from loguru import logger

import tf2mon
from tf2mon.admin import Admin
from tf2mon.conlog import Conlog
from tf2mon.database import Database
from tf2mon.gameplay import Gameplay
from tf2mon.pkg import APPNAME
from tf2mon.player import Player
from tf2mon.racist import load_racist_data
from tf2mon.regex import Regex
from tf2mon.role import load_weapons_data
from tf2mon.steamplayer import SteamPlayer
from tf2mon.ui import UI
from tf2mon.users import Users


class Monitor:
    """Team Fortress 2 Console Monitor."""

    _regex_list: list[Regex] = []
    _admin = Admin()
    _gameplay = Gameplay()

    def run(self):
        """Run the Monitor."""
        libcurses.wrapper(self._run)

    def _run(self, win: curses.window) -> None:
        """Complete initialization; post CLI, options now available."""

        tf2mon.conlog = Conlog(tf2mon.options)
        load_weapons_data(Path(__file__).parent / "data" / "weapons.csv")
        load_racist_data(Path(__file__).parent / "data" / "racist.txt")
        self._regex_list += self._admin.regex_list
        self._regex_list += self._gameplay.regex_list
        self._regex_list += tf2mon.controller.get_regex_list()
        tf2mon.ui = UI(win)
        Users.me = Users.my = Users[tf2mon.config.get("player_name")]
        tf2mon.controller.start()
        tf2mon.reset_game()

        # no need for threads if exiting at end of conlog
        if not tf2mon.options.follow:
            self.game()
            return

        # Read from conlog, write to display.
        thread = threading.Thread(name="GAME", target=self.game, daemon=True)
        thread.start()

        # Read from keyboard/mouse, write to display.
        self.admin()

    def game(self):
        """Read console log file and play game."""

        Database(tf2mon.options.database, [Player, SteamPlayer])
        tf2mon.conlog.open()  # waits until it exists; then opens and returns.
        stepper = tf2mon.SingleStepControl

        while (line := tf2mon.conlog.readline()) is not None:
            if not line:
                continue

            regex = Regex.search_list(line, self._regex_list)
            if not regex:
                logger.log("ignore", tf2mon.conlog.last_line)
                continue

            # start single stepping if pattern match
            if not stepper.is_stepping and stepper.pattern and stepper.pattern.search(line):
                pattern = stepper.pattern.pattern
                flags = "i" if (stepper.pattern.flags & re.IGNORECASE) else ""
                logger.log("ADMIN", f"break search /{pattern}/{flags}")
                stepper.start_single_stepping()

            level = "nextline" if stepper.is_stepping else "logline"
            logger.log(level, "-" * 80)
            logger.log(level, tf2mon.conlog.last_line)

            # check gate
            stepper.wait()
            if stepper.is_stepping:
                stepper.clear()

            regex.handler(regex.re_match_obj)
            tf2mon.MsgQueuesControl.send()
            tf2mon.ui.update_display()

    def admin(self) -> None:
        """Admin console read-evaluate-process-loop."""

        while not tf2mon.conlog.is_eof or tf2mon.options.follow:

            tf2mon.ui.update_display()

            prompt = APPNAME
            if tf2mon.SingleStepControl.is_stepping:
                prompt += " (single-stepping)"
            prompt += ": "

            if (line := tf2mon.ui.getline(prompt)) is None:
                logger.log("console", "quit eof")
                return

            if line == "":  # enter
                if tf2mon.conlog.is_eof:
                    logger.log("console", f"lineno={tf2mon.conlog.lineno} <EOF>")
                # else:
                #     logger.trace("step...")
                tf2mon.SingleStepControl.set()
                continue

            logger.log("console", f"line={line!r}")

            cmd = line  # .upper()
            if "quit".find(cmd) == 0:
                logger.log("console", "quit")
                return

            if regex := Regex.search_list(cmd, self._admin.regex_list):
                regex.handler(regex.re_match_obj)
            else:
                logger.error(f"bad admin command {cmd!r}")
