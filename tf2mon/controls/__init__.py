"""Collection of `Control`s."""

from loguru import logger

from tf2mon.command import Command, CommandManager
from tf2mon.control import Control
from tf2mon.fkey import FKey


class Controller:
    """Collection of `Control`s."""

    controls: list[Control] = []
    debug = False

    commands = CommandManager()
    get_regex_list = commands.get_regex_list
    get_status_line = commands.get_status_line

    def add(self, control: Control, keyspec: str = None, game_only: bool = False) -> None:
        """Add control to collection; optionally bind to `keyspec`."""

        if keyspec is not None:
            control.fkey = FKey(keyspec)
        if self.debug:
            logger.debug(control)
        self.controls.append(control)

        if keyspec is None:
            return

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
        for control in [x for x in self.controls if x.fkey]:
            # 17 == indent 4 + len("KP_RIGHTARROW")
            lines.append(f"{control.fkey.keyspec:>17} {control.__doc__}")
        return "\n".join(lines)

    def start(self) -> None:
        """Finalize initialization now that curses has been started."""

        self.commands.register_curses_handlers()

        for control in [x for x in self.controls if hasattr(x, "start")]:
            if self.debug:
                logger.debug(control)
            control.start()
