"""Team Fortress 2 Console Monitor."""

import curses
import re
import threading
from pathlib import Path

import libcurses
from loguru import logger

import tf2mon
import tf2mon.game
from tf2mon.conlog import Conlog
from tf2mon.database import Database
from tf2mon.pkg import APPNAME
from tf2mon.player import Player
from tf2mon.racist import load_racist_data
from tf2mon.role import load_weapons_data
from tf2mon.steamplayer import SteamPlayer
from tf2mon.ui import UI


class Monitor:
    """Team Fortress 2 Console Monitor."""

    def run(self) -> None:
        """Run the Monitor."""
        libcurses.wrapper(self._run)

    def _run(self, win: curses.window) -> None:
        """Complete initialization; post CLI, options now available."""

        tf2mon.conlog = Conlog(tf2mon.options)
        load_weapons_data(Path(__file__).parent / "data" / "weapons.csv")
        load_racist_data(Path(__file__).parent / "data" / "racist.txt")
        tf2mon.ui = UI(win)
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

    def game(self) -> None:
        """Read console log file and play game."""

        Database(tf2mon.options.database, [Player, SteamPlayer])
        assert tf2mon.conlog
        tf2mon.conlog.open()  # waits until it exists; then opens and returns.
        stepper = tf2mon.SingleStepControl

        while (line := tf2mon.conlog.readline()) is not None:
            # conlog.readline does not return excluded lines.
            if not line:
                continue

            event, match = None, None
            for event in [
                x
                for x in tf2mon.game.events + tf2mon.controller.controls
                if hasattr(x, "search") and x.search
            ]:
                assert event.search
                if match := event.search(line):
                    break
            else:
                logger.log("ignore", tf2mon.conlog.last_line)
                continue

            logger.log("regex", match)

            if hasattr(event, "start_stepping") and event.start_stepping:
                logger.log("ADMIN", f"break on {event.__class__.__name__}")
                stepper.start_single_stepping()

            elif stepper.pattern and stepper.pattern.search(line):
                pattern = stepper.pattern.pattern
                flags = "i" if (stepper.pattern.flags & re.IGNORECASE) else ""
                logger.log("ADMIN", f"break search /{pattern}/{flags}")
                stepper.start_single_stepping()

            level = "nextline" if stepper.is_stepping else "logline"
            logger.log(level, "-" * 80)
            logger.log(level, tf2mon.conlog.last_line)

            # check gate
            assert stepper.wait
            stepper.wait(None)
            if stepper.is_stepping:
                assert stepper.clear
                stepper.clear()

            if hasattr(event, "handler"):
                event.handler(match)
                tf2mon.MsgQueuesControl.send()
                tf2mon.ui.update_display()

    def admin(self) -> None:
        """Admin console read-evaluate-process-loop."""

        # pylint: disable=too-many-branches

        stepper = tf2mon.SingleStepControl
        assert stepper
        assert tf2mon.conlog

        while not tf2mon.conlog.is_eof or tf2mon.options.follow:

            tf2mon.ui.update_display()

            prompt = APPNAME
            if stepper.is_stepping:
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
                assert stepper.set
                stepper.set()
                continue

            logger.log("console", f"line={line!r}")

            if "quit".find(line) == 0:
                logger.log("console", "quit")
                return

            try:
                cmd, arg = line.split(maxsplit=1)
            except ValueError:
                cmd = line
                arg = None

            if "breakpoint".find(cmd) == 0 and arg and arg.isdigit():
                stepper.set_single_step_lineno(int(arg))

            elif cmd[0] == "/":
                pattern = cmd[1:]
                if arg:
                    pattern += f" {arg}"
                stepper.set_single_step_pattern(pattern)

            elif "continue".find(cmd) == 0 or "go".find(cmd) == 0 or "run".find(cmd) == 0:
                stepper.stop_single_stepping()

            elif "kick".find(cmd) == 0 and arg and arg.isdigit():
                tf2mon.users.kick_userid(int(arg), Player.CHEATER)

            elif "kkk".find(cmd) == 0 and arg and arg.isdigit():
                tf2mon.users.kick_userid(int(arg), Player.RACIST)

            elif "suspect".find(cmd) == 0 and arg and arg.isdigit():
                tf2mon.users.kick_userid(int(arg), Player.SUSPECT)

            elif "dump".find(cmd) == 0:
                tf2mon.dump()

            elif "help".find(cmd) == 0:
                tf2mon.HelpControl.handler(None)

            elif "motd".find(cmd) == 0:
                tf2mon.MotdControl.handler(None)

            elif "pdb".find(cmd) == 0:
                tf2mon.debugger()

            else:
                logger.error(f"bad admin command {cmd!r}")
