"""Application control."""

import argparse
from typing import Callable

from libcli import BaseCLI

import tf2mon
from tf2mon.command import Command
from tf2mon.fkey import FKey
from tf2mon.toggle import Toggle


class Control:
    """Application control.

    Optional methods that derived classes MAY define:
    :g/[gh]..attr/p

        status
            Return current value as `str` formatted for display.

        handler
            Perform monitor function.

        action
            Game "script" text to `exec`.

        add_arguments_to
            Add control to cli `parser`.

        start
            Start using curses/user-interface.
            Finalize initialization after curses has been started.
            ...

    """

    command: Command = None

    # Optional; function key to operate control.
    fkey: FKey = None

    #
    cli: BaseCLI = None

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"

    def add_fkey_to_help(self, arg: argparse.Action) -> None:
        """Add 'FKey.label` to help text for `arg`."""

        if not self.fkey:
            return
        text = f" (fkey: `{self.fkey.label}`)"
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
