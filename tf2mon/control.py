"""Application control."""

import argparse
import re
from typing import Callable, ClassVar

from libcli import BaseCLI

import tf2mon
from tf2mon.fkey import FKey
from tf2mon.pkg import APPTAG
from tf2mon.toggle import Toggle


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

    controls_by_key: ClassVar[dict[int, "Control"]] = {}
    pkeys: dict[str, FKey] = {}

    name: str = None  # token
    # status: Callable[..., str] = None
    # handler: Callable[[re.Match], None] = None
    action: str = None

    # Optional; function key to operate control.
    fkey: FKey = None

    #
    cli: ClassVar[BaseCLI] = None

    def __init__(self):
        """Init."""

        if self.name:
            # Default action, have game send this event notification
            # message to monitor whenever game calls for this command,
            # such as in response to an in-game key-press or mouse-click.
            token = APPTAG + self.name
            if not self.action:
                self.action = f"echo {token}"
            self.pattern = f"^{token}$"
            self._re = re.compile(self.pattern)
            self.match = self._re.match
            self.search = self._re.search
        else:
            self.match = lambda _line: False
            self.search = lambda _line: False

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"

    def add_fkey_to_help(self, arg: argparse.Action) -> None:
        """Add fkey to help text for `arg`."""

        if not self.fkey:
            return
        text = f" (fkey: `{self.fkey.longname}`)"
        if arg.help.endswith(self.cli.help_line_ending):
            arg.help = (
                arg.help[: -len(self.cli.help_line_ending)] + text + self.cli.help_line_ending
            )
        else:
            arg.help += text

    def toggling_enabled(self) -> bool:
        """Return True if toggling is enabled.

        Don't allow toggling when replaying a game (`--rewind`),
        unless `--toggles` is also given... or if single-stepping

        This is checked by keys that alter the behavior of gameplay;
        it is not checked by keys that only alter the display.
        """

        return (
            tf2mon.conlog.is_eof
            or tf2mon.options.toggles
            or tf2mon.SingleStepControl.is_stepping
        )


class BoolControl(Control):
    """Bool control."""

    toggle: Toggle = None

    def handler(self, _match) -> None:
        """Handle event."""

        if self.toggling_enabled():
            _ = self.toggle.toggle
            tf2mon.ui.show_status()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.toggle.name.upper() if self.toggle.value else self.toggle.name

    @property
    def value(self) -> bool:
        """Return value."""

        return self.toggle.value


class CycleControl(Control):
    """Cycle control."""

    toggle: Toggle = None
    items: dict = {}

    def status(self) -> str:
        """Return value formatted for display."""

        return self.toggle.value.name

    @property
    def value(self) -> Callable:
        """Return value."""

        return self.items[self.toggle.value]
