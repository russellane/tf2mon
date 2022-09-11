"""Application controls."""

from tf2mon.command import Command, CommandManager
from tf2mon.control import Control
from tf2mon.fkey import FKey


class Controls:
    """Collection of `Control`s."""

    controls: list[Control] = []
    bindings: list[Control] = []

    commands = CommandManager()
    get_regex_list = commands.get_regex_list
    get_status_line = commands.get_status_line

    def bind(self, control: Control, keyspec: str = None, game_only: bool = False) -> None:
        """Bind `control` to `keyspec`."""

        self.controls.append(control)
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
        for control in self.controls:
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

        for control in [x for x in self.controls if hasattr(x, "start")]:
            control.start()
