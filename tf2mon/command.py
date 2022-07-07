"""Command.

May be invoked by:
    - keypress within game.
    - keypress within monitor.
    - commands typed into game console (`~`).
    - commands typed into monitor admin repl.
"""

import re
import time
from dataclasses import dataclass, field
from typing import Callable

from libcurses import register_fkey

from tf2mon import APPNAME, APPTAG
from tf2mon.fkey import FKey
from tf2mon.regex import Regex


@dataclass
class Command:
    """Command.

    Attributes:
        name: str
            Command name; e.g., 'HELP', 'TOGGLE-SORT'.

        status: Callable[..., str]
            must return current value as `str` for display;
            Default `None` to hide.

        handler: Callable[re.Match, None]
            must perform monitor function; Default `None` for no-op. e.g.,
            cmd="PULL", only has a game function to perform (which is to
            push `status`... it's pull from the monitor's perspective.)

        action: str
            game action to `exec`; e.g., cmd="KICKS-POP" has
            action="tf2mon_kicks_pop". Default `None` causes game to send
            event notice to monitor. e.g., cmd='TOGGLE-SORT' only has a
            monitor function to perform.

    """

    name: str
    status: Callable[..., str] = None
    handler: Callable[re.Match, None] = None
    action: str = None

    def __post_init__(self):
        """Init."""

        if not self.action:
            # Default, have game send this event notification message to
            # monitor whenever game calls for this command, such as in
            # response to an in-game key-press or mouse-click.
            self.action = f"echo {APPTAG}{self.name}"

    @property
    def request_pattern(self) -> str:
        """Return pattern to detect request from game to invoke this command."""

        # anchor head, optional timestamp, token, anchor tail.
        return r"^(\d{2}/\d{2}/\d{4} - \d{2}:\d{2}:\d{2}: )?" f"{APPTAG}{self.name}$"


@dataclass
class Function:
    """An `FKey`/`Command` binding."""

    keystroke: FKey
    command: Command

    def __repr__(self):
        return str(self.__dict__)


@dataclass
class Key:
    """A physical key may perform `base`, `ctrl` and `shift` `Function`s."""

    name: str  # e.g., "A", "F1"
    base: Function = field(default=None, init=False)
    ctrl: Function = field(default=None, init=False)
    shift: Function = field(default=None, init=False)

    @property
    def functions(self) -> [Function]:
        """Return list of `Functions` bound to this `Key`."""
        return [x for x in [self.base, self.ctrl, self.shift] if x is not None]


class CommandManager:
    """Command manager."""

    def __init__(self):
        """Init."""

        self.key_by_name: dict[str, Key] = {}

    def bind(
        self,
        cmd_factory: Callable[..., Command],
        keyspec: str,
        game_only: bool = False,
    ) -> None:
        """Bind `Command` returned by `cmd_factory` with `keyspec`."""

        command = cmd_factory()
        if game_only:
            command.handler = None

        keystroke = FKey(keyspec)
        if (key := self.key_by_name.get(keystroke.name)) is None:
            key = Key(keystroke.name)

        function = Function(keystroke, command)

        if keystroke.is_ctrl:
            if key.ctrl:
                raise ValueError("duplicate keyspec", keyspec)
            key.ctrl = function
        #
        elif keystroke.is_shift:
            if key.shift:
                raise ValueError("duplicate keyspec", keyspec)
            key.shift = function
        #
        else:
            if key.base:
                raise ValueError("duplicate keyspec", keyspec)
            key.base = function

        self.key_by_name[keystroke.name] = key

    def as_tf2_exec_script(self) -> str:
        """Return game key bindings as TF2 exec script."""

        lines = [
            f"// Created by {APPNAME} on {time.asctime()}",
            "",
            "// Bind unmodified keys directly to their `base` commands.",
            "",
        ]

        for key in [
            x for x in self.key_by_name.values() if x.name and x.base and not (x.ctrl or x.shift)
        ]:
            if key.base.command.action:
                lines.append(f'bind "{key.name}" "{key.base.command.action}"')

        lines.extend(
            [
                "",
                "// Bind modified keys indirectly through aliases.",
                "",
            ]
        )

        _base, _ctrl, _shift = [], [], []

        for key in [x for x in self.key_by_name.values() if x.name and (x.ctrl or x.shift)]:
            if key.base and key.base.command.action:
                alias = f"_b{key.name}"
                lines.append(f'alias "{alias}" "{key.base.command.action}"')
                _base.append(f"bind {key.name} {alias}")

            if key.ctrl and key.ctrl.command.action:
                alias = f"_c{key.name}"
                lines.append(f'alias "{alias}" "{key.ctrl.command.action}"')
                _ctrl.append(f"bind {key.name} {alias}")

            if key.shift and key.shift.command.action:
                alias = f"_s{key.name}"
                lines.append(f'alias "{alias}" "{key.shift.command.action}"')
                _shift.append(f"bind {key.name} {alias}")

        lines.extend(
            [
                "",
                "// Toggle modified keys.",
                "",
            ]
        )

        # alias _bind_base "bind f1 _bf1; bind f2 _bf2; bind f3 _bf3; bind f4 _bf4"
        # alias _bind_ctrl "bind f1 _cf1; bind f2 _cf2; bind f3 _cf3; bind f4 _cf4"
        # alias _bind_shift "bind f1 _sf1; bind f2 _sf2; bind f3 _sf3; bind f4 _sf4"

        if binds := "; ".join(_base):
            lines.append(f'alias _bind_base "{binds}"')

        if binds := "; ".join(_ctrl):
            lines.append(f'alias _bind_ctrl "{binds}"')

        if binds := "; ".join(_shift):
            lines.append(f'alias _bind_shift "{binds}"')

        lines.extend(
            [
                "",
                'bind ctrl "+ctrled"',
                "alias +ctrled _bind_ctrl",
                "alias -ctrled _base_base",
                "",
                'bind shift "+shifted"',
                "alias +shifted _bind_shift",
                "alias -shifted _bind_base",
                "",
                "_bind_base",
            ]
        )

        return "\n".join(lines)

    def register_curses_handlers(self):
        """Register curses key handlers."""

        for key in self.key_by_name.values():
            for function in key.functions:
                if function.command.handler:
                    register_fkey(function.command.handler, function.keystroke.key)

    def get_regex_list(self):
        """Return list of `Regex` for all handlers."""

        items = []
        for key in self.key_by_name.values():
            for function in key.functions:
                if function.command.handler:
                    items.append(
                        Regex(function.command.request_pattern, function.command.handler)
                    )
        return items

    def get_status_line(self):
        """Return 1-line string showing current state of function keys."""

        items = []
        for key in self.key_by_name.values():
            for function in key.functions:
                if function.command.status:
                    items.append(f"{function.keystroke.label}={function.command.status()}")
        return " ".join(items)
