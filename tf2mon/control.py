"""Application control."""

import argparse
import importlib
import pkgutil

from libcli import BaseCLI

import tf2mon
from tf2mon.command import Command, CommandManager
from tf2mon.fkey import FKey


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


class BoolControl(Control):
    """Bool control."""

    toggle = None

    def handler(self, _match) -> None:
        """Handle event."""

        if tf2mon.monitor.toggling_enabled:
            _ = self.toggle.toggle
            tf2mon.monitor.ui.show_status()

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
    bindings: list[Control] = []

    commands = CommandManager()
    get_regex_list = commands.get_regex_list
    get_status_line = commands.get_status_line

    def __init__(
        self,
        modname: str,
        prefix: str = None,
        suffix: str = None,
    ) -> None:
        """Add all `Control`s in module `modname`."""

        modpath = importlib.import_module(modname, __name__).__path__
        base_name = (prefix or "") + (suffix or "")

        for modinfo in pkgutil.iter_modules(modpath):
            module = importlib.import_module(f"{modname}.{modinfo.name}", __name__)

            if not prefix and not suffix and hasattr(module, "Control"):
                module.Control()
                continue

            for name in [x for x in dir(module) if x != base_name]:
                if prefix and not name.startswith(prefix):
                    continue
                if suffix and not name.endswith(suffix):
                    continue
                if (klass := getattr(module, name, None)) is not None:
                    self.add(klass())

    def __getitem__(self, name: str) -> Control:
        """Return the `Control` known as `name`."""

        return self.items[name]

    def add(self, control: Control) -> None:
        """Add `control`, known as its class name, to collection."""

        self.items[control.__class__.__name__] = control

    def bind(self, name: str, keyspec: str = None, game_only: bool = False) -> None:
        """Bind the control known as `name` to `keyspec`."""

        control = self.items[name]
        self.bindings.append(control)
        control.fkey = FKey(keyspec)

        control.command = Command(
            control.name,
            getattr(control, "status", None),
            getattr(control, "handler", None),
            getattr(control, "action", None),
        )
        self.commands.bind(control.command, keyspec, game_only)

    def add_arguments_to(self, parser) -> None:
        """Add arguments for all controls to `parser`."""

        cli = parser.get_default("cli")
        for control in self.items.values():
            if hasattr(control, "add_arguments_to"):
                control.cli = cli
                control.add_arguments_to(parser)

    def fkey_help(self) -> str:
        """Return help for function keys."""

        lines = []
        for control in self.bindings:
            # 17 == indent 4 + len("KP_RIGHTARROW")
            lines.append(f"{control.fkey.keyspec:>17} {control.__doc__}")
        return "\n".join(lines)

    def start(self) -> None:
        """Finalize initialization now that curses has been started."""

        self.commands.register_curses_handlers()

        for control in [x for x in self.items.values() if hasattr(x, "start")]:
            control.start()
