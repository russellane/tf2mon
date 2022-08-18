"""Application controls."""

import importlib
import pkgutil

from tf2mon.command import Command, CommandManager
from tf2mon.control import Control
from tf2mon.fkey import FKey


class Controls:
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
