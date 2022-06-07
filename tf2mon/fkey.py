"""Monitor Commands and their Function Keys."""

import curses
import time

import libcurses

from tf2mon.hacker import HackerAttr
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

    cmd_prefix: str = None

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
        self.action = action or f"echo {self.cmd_prefix}{cmd}"

        # how to recognize tf2 performing this action in the con_logfile.
        leader = (
            r"^(\d{2}/\d{2}/\d{4} - \d{2}:\d{2}:\d{2}: )?"  # anchor to head; optional timestamp
        )
        self.regex = Regex(leader + f"{self.cmd_prefix}{cmd}$", handler) if handler else None


class FKeyManager:
    """Collection of `FKey` objects."""

    def __init__(self, monitor):
        """Initialize command and function key bindings."""

        FKey.cmd_prefix = monitor.cmd_prefix
        self.monitor = monitor
        self._fkeys = self._load_fkeys()

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

    def _load_fkeys(self):
        def _on_off(k, v):
            return k.upper() if v else k

        return [
            FKey(
                cmd="HELP",
                game_key="F1",
                curses_key=curses.KEY_F1,
                status=lambda: "HELP",
                handler=lambda m: self.monitor.ui.show_help(),
            ),
            FKey(
                cmd="TOGGLE-DEBUG",
                game_key="F2",
                curses_key=curses.KEY_F2,
                status=lambda: _on_off("debug", self.monitor.ui.debug_flag.value),
                handler=lambda m: (
                    self.monitor.ui.debug_flag.toggle,
                    self.monitor.ui.show_status(),
                ),
            ),
            FKey(
                cmd="TOGGLE-TAUNT",
                game_key="F3",
                curses_key=curses.KEY_F3,
                status=lambda: _on_off("taunt", self.monitor.ui.taunt_flag.value),
                handler=lambda m: (
                    self.monitor.ui.taunt_flag.toggle,
                    self.monitor.ui.show_status(),
                ),
            ),
            FKey(
                cmd="TOGGLE-KD",
                game_key="F4",
                curses_key=curses.KEY_F4,
                status=lambda: _on_off("kd", self.monitor.ui.show_kd.value),
                handler=lambda m: (
                    self.monitor.ui.show_kd.toggle,
                    self.monitor.ui.show_status(),
                ),
            ),
            FKey(
                cmd="TOGGLE-USER-PANEL",
                game_key="F5",
                curses_key=curses.KEY_F5,
                status=lambda: self.monitor.ui.user_panel.value.name,
                handler=lambda m: (
                    self.monitor.ui.user_panel.toggle,
                    self.monitor.ui.update_display(),
                ),
            ),
            FKey(
                cmd="SWITCH-MY-TEAM",
                game_key="F6",
                curses_key=curses.KEY_F6,
                status=lambda: self.monitor.my.team.name if self.monitor.my.team else "blu",
                handler=lambda m: (
                    self.monitor.me.assign_team(self.monitor.my.opposing_team),
                    self.monitor.ui.update_display(),
                ),
            ),
            FKey(
                cmd="TOGGLE-SORT",
                game_key="F7",
                curses_key=curses.KEY_F7,
                status=lambda: self.monitor.ui.sort_order.value.name,
                handler=lambda m: (
                    self.monitor.ui.set_sort_order(self.monitor.ui.sort_order.toggle),
                    self.monitor.ui.update_display(),
                ),
            ),
            FKey(
                cmd="TOGGLE-LOG-LOCATION",
                game_key="F8",
                curses_key=curses.KEY_F8,
                status=lambda: self.monitor.ui.log_location.value.name,
                handler=lambda m: (
                    self.monitor.ui.cycle_log_location(),
                    self.monitor.ui.show_status(),
                ),
            ),
            FKey(
                cmd="TOGGLE-GRID-LAYOUT",
                game_key="F9",
                curses_key=curses.KEY_F9,
                status=lambda: self.monitor.ui.grid_layout.value.name,
                handler=lambda m: self.monitor.ui.cycle_grid_layout(),
            ),
            FKey(
                cmd="SINGLE-STEP",
                game_key="KP_DEL",
                curses_key=curses.KEY_DC,
                handler=lambda m: self.monitor.admin.start_single_stepping(),
            ),
            FKey(
                cmd="KICK-LAST-CHEATER",
                game_key="[",
                curses_key=None,
                status=lambda: HackerAttr.CHEATER.name,
                handler=lambda m: self.monitor.kick_my_last_killer(HackerAttr.CHEATER),
            ),
            FKey(
                cmd="KICK-LAST-RACIST",
                game_key="]",
                curses_key=None,
                status=lambda: HackerAttr.RACIST.name,
                handler=lambda m: self.monitor.kick_my_last_killer(HackerAttr.RACIST),
            ),
            FKey(
                cmd="KICK-LAST-SUSPECT",
                game_key="\\",
                curses_key=None,
                status=lambda: HackerAttr.SUSPECT.name,
                handler=lambda m: self.monitor.kick_my_last_killer(HackerAttr.SUSPECT),
            ),
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
            # kicks
            FKey(
                cmd="KICKS-POP",
                game_key="KP_HOME",
                curses_key=curses.KEY_HOME,
                handler=lambda m: self.monitor.kicks.pop(),
                action="tf2mon_kicks_pop",
            ),
            FKey(
                cmd="KICKS-CLEAR",
                game_key="KP_LEFTARROW",
                curses_key=curses.KEY_LEFT,
                handler=lambda m: self.monitor.kicks.clear(),
                action="tf2mon_kicks_clear",
            ),
            FKey(
                cmd="KICKS-POPLEFT",
                game_key="KP_END",
                curses_key=curses.KEY_END,
                handler=lambda m: self.monitor.kicks.popleft(),
                action="tf2mon_kicks_popleft",
            ),
            # admin
            FKey(
                cmd="PULL",
                game_key="KP_UPARROW",
                curses_key=curses.KEY_UP,
                # handler=lambda m: logger.trace('pull'),
                action="tf2mon_pull",
            ),
            FKey(
                cmd="CLEAR-QUEUES",
                game_key="KP_5",
                curses_key=curses.KEY_B2,
                handler=lambda m: self.monitor.msgqueues.clear(),
                action="tf2mon_clear_queues",
            ),
            FKey(
                cmd="PUSH",
                game_key="KP_DOWNARROW",
                curses_key=curses.KEY_DOWN,
                # handler=lambda m: logger.trace('push'),
                action="tf2mon_push",
            ),
            # spams
            FKey(
                cmd="SPAMS-POP",
                game_key="KP_PGUP",
                curses_key=curses.KEY_PPAGE,
                handler=lambda m: self.monitor.spams.pop(),
                action="tf2mon_spams_pop",
            ),
            FKey(
                cmd="SPAMS-CLEAR",
                game_key="KP_RIGHTARROW",
                curses_key=curses.KEY_RIGHT,
                handler=lambda m: self.monitor.spams.clear(),
                action="tf2mon_spams_clear",
            ),
            FKey(
                cmd="SPAMS-POPLEFT",
                game_key="KP_PGDN",
                curses_key=curses.KEY_NPAGE,
                handler=lambda m: self.monitor.spams.popleft(),
                action="tf2mon_spams_popleft",
            ),
        ]
