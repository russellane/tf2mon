"""Application control."""

import argparse

from libcli import BaseCLI

from tf2mon.command import CommandManager
from tf2mon.fkey import FKey


class Control:
    """Application control."""

    # Controls are created before the monitor and its ui.
    monitor = None

    # Optional; function key to operate control.
    fkey: FKey = None

    #
    cli: BaseCLI = None

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


class BoolControl(Control):
    """Bool control."""

    toggle = None

    def handler(self, _match) -> None:
        """Handle event."""

        if self.monitor.toggling_enabled:
            _ = self.toggle.toggle
            self.monitor.ui.show_status()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.toggle.name.upper() if self.toggle.value else self.toggle.name

    @property
    def value(self) -> bool:
        """Return value."""

        return self.toggle.value


class CycleControl(Control):
    """Cycle control."""

    toggle = None
    items = {}

    def status(self) -> str:
        """Return value formatted for display."""

        return self.toggle.value.name

    @property
    def value(self) -> callable:
        """Return value."""

        return self.items[self.toggle.value]


class ControlManager:
    """Collection of `Control`s."""

    items: dict[str, Control] = {}
    commands = CommandManager()

    def __getitem__(self, name: str) -> Control:
        """Return the `Control` known as `name`."""

        return self.items[name]

    def add(self, control: Control) -> None:
        """Add `control`, known as its class name, to collection."""

        self.items[control.__class__.__name__] = control

    def bind(self, name: str, keyspec: str = None, game_only: bool = False) -> None:
        """Bind the control known as `name` to `keyspec`."""

        control = self.items[name]
        control.fkey = FKey(keyspec)
        self.commands.bind(control, keyspec, game_only)

    def add_arguments_to(self, parser) -> None:
        """Add arguments for all controls to `parser`."""

        cli = parser.get_default("cli")
        for control in self.items.values():
            if hasattr(control, "add_arguments_to"):
                control.cli = cli
                control.add_arguments_to(parser)
