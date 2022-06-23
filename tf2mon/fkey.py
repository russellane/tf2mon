"""Monitor Commands and their Function Keys."""

import time

import libcurses

import tf2mon
from tf2mon.regex import Regex


class FKey:
    """Monitor Commands and their Function Keys."""

    # A command may be invoked by:
    #   1. keypress within game
    #   2. keypress within monitor
    #   3. commands typed into the game console
    #   4. commands typed into the monitor console

    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        cmd=None,
        game_key=None,
        curses_key=None,
        status=None,
        handler=None,
        action=None,
        doc=None,
    ):
        """Create fkey-driven monitor command.

        Create a function to be performed when key is pressed in monitor and/or in game.

        Args:
            cmd:        command name; 'HELP', 'TOGGLE-SORT', etc.

            game_key:   key to run command from within game; 'F1'.

            curses_key: key to run command from monitor console; curses.KEY_F1.

            status:     callable returning printable current value.

            handler:    action to take when game or admin key is pressed;
                        must take 1 argument: re_match_obj.

            action:     Commands with an `action` (eg cmd='KICKS-POP' has
                        action='tf2mon_kicks_pop') are bound to run their
                        actions. Commands without an `action` (eg
                        cmd='TOGGLE-SORT' has action=None) are bound to
                        echo the command name to us (eg, "echo TF2MON-
                        TOGGLE-SORT").

            doc:        Documentation.
        """

        # pylint: disable=too-many-arguments

        self.cmd = cmd
        self.game_key = game_key
        self.curses_key = curses_key
        self.status = status
        self.handler = handler
        self.doc = doc

        # configure tf2 to perform this action when key is pressed.
        self.action = action or f"echo {tf2mon.APPTAG}{cmd}"

        # how to recognize tf2 performing this action in the con_logfile.
        leader = (
            r"^(\d{2}/\d{2}/\d{4} - \d{2}:\d{2}:\d{2}: )?"  # anchor to head; optional timestamp
        )
        self.regex = Regex(leader + f"{tf2mon.APPTAG}{cmd}$", handler) if handler else None


class FKeyManager:
    """Collection of `FKey` objects."""

    def __init__(self):
        """Initialize command and function key bindings."""

        self._fkeys = []

    def add(self, fkey: FKey) -> None:
        """Add `fkey` to collection."""

        self._fkeys.append(fkey)

    def create_tf2_exec_script(self, path):
        """Create tf2 exec script of keyboard BIND commands.

        Args:
            path:   tf2 exec script to create.
        """

        # write game key bindings to tf2 exec script
        with open(path, "w", encoding="utf-8") as file:
            print(f"// auto-generated {time.asctime()}", file=file)
            print(
                "\n".join(
                    [f'bind "{x.game_key}" "{x.action}"' for x in self._fkeys if x.game_key]
                ),
                file=file,
            )

    def register_curses_handlers(self):
        """Register curses key handlers."""

        for fkey in [x for x in self._fkeys if x.handler and x.curses_key]:
            libcurses.register_fkey(fkey.handler, fkey.curses_key)

    def get_regex_list(self):
        """Return list of `Regex` for all handlers."""

        return [x.regex for x in self._fkeys if x.regex]

    def get_status_line(self):
        """Return 1-line string showing current state of function keys."""

        return " ".join([x.game_key + "=" + x.status() for x in self._fkeys if x.status])

    def get_help(self) -> str:
        """Return formatted help text for man page."""

        doc = "These function keys are available in-game and in the monitor:\n"

        for fkey in [x for x in self._fkeys if x.doc]:
            doc += f"    {fkey.game_key}={fkey.doc}\n"

        return doc
