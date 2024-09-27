"""Application control."""

from __future__ import annotations

import argparse
import re
from typing import Any, ClassVar, Match

from libcli import BaseCLI

import tf2mon
from tf2mon.cycle import Cycle
from tf2mon.fkey import FKey
from tf2mon.pkg import APPTAG


class Control:
    """Application control.

    Optional methods that derived classes MAY define:
    :g/[gh]..attr/p

    CONTROL -
        status
            Return current value as `str` formatted for display.
            Default `None` to hide.

        handler
            Perform monitor function.

        name
            Command name; e.g., 'HELP', 'TOGGLE-SORT'.

        action
            Game "script" text to `exec`.

        add_arguments_to
            Add control to cli `parser`.

        start
            Finalize initialization after curses has been started.
    """

    pkeys: dict[str, FKey] = {}

    name: str = ""  # token
    # status: Callable[..., str] = None
    # handler: Callable[[re.Match], None] = None
    action: str = ""

    # Optional; function key to operate control.
    fkey: FKey | None = None

    #
    cli: ClassVar[BaseCLI]

    #
    match = None
    search = None

    def __init__(self) -> None:
        """Init."""

        if self.name:
            # Default action, have game send this event notification
            # message to monitor whenever game calls for this command,
            # such as in response to an in-game key-press or mouse-click.
            token = APPTAG + self.name
            if not self.action:
                self.action = f"echo {token}"
            pattern = f"^{token}$"
            self._re = re.compile(pattern)
            self.match = self._re.match
            self.search = self._re.search

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"

    def add_fkey_to_help(self, arg: argparse.Action) -> None:
        """Add fkey to help text for `arg`."""

        if not self.fkey:
            return
        text = f" (fkey: `{self.fkey.longname}`)"
        assert arg.help
        assert self.cli
        if arg.help.endswith(self.cli.help_line_ending):
            arg.help = (
                arg.help[: -len(self.cli.help_line_ending)] + text + self.cli.help_line_ending
            )
        else:
            arg.help += text

    def toggling_enabled(self) -> bool:
        """Return True if toggling is enabled.

        Don't allow toggling when replaying a game (`--rewind`),
        unless `--allow-toggles` is also given... or if single-stepping

        This is checked by keys that alter the behavior of gameplay;
        it is not checked by keys that only alter the display.
        """

        assert tf2mon.conlog

        return (
            tf2mon.conlog.is_eof
            or tf2mon.options.allow_toggles
            or tf2mon.SingleStepControl.is_stepping
        )


class BoolControl(Control):
    """Bool control."""

    cycle: Cycle

    def handler(self, _match: Match[str] | None) -> None:
        """Handle event."""

        if self.toggling_enabled():
            _ = self.cycle.next
            tf2mon.ui.show_status()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.cycle.name.upper() if self.cycle.value else self.cycle.name

    @property
    def value(self) -> bool:
        """Return value."""

        return bool(self.cycle.value)


class CycleControl(Control):
    """Cycle control."""

    cycle: Cycle
    items: dict[Any, Any] = {}

    def status(self) -> str:
        """Return value formatted for display."""

        return str(self.cycle.value.name)

    @property
    def value(self) -> Any:
        """Return value."""

        return self.items[self.cycle.value]
