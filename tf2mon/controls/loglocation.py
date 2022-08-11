"""Format of logger location field."""

from enum import Enum

from tf2mon.command import Command
from tf2mon.control import Control
from tf2mon.toggle import Toggle


class LogLocationControl(Control):
    """Format of logger location field."""

    name = "TOGGLE-LOG-LOCATION"

    ENUM = Enum("_loc_enum", "MOD NAM THM THN FILE NUL")
    TOGGLE = Toggle("_loc_toggle", ENUM)
    ITEMS = {
        ENUM.MOD: "{module}.{function}:{line}",
        ENUM.NAM: "{name}.{function}:{line}",
        ENUM.THM: "{thread.name}:{module}.{function}:{line}",
        ENUM.THN: "{thread.name}:{name}.{function}:{line}",
        ENUM.FILE: "{file}:{function}:{line}",
        ENUM.NUL: None,
    }

    #
    def start(self, value: str) -> None:
        """Set to `value`."""

        self.TOGGLE.start(self.ENUM.__dict__[value])
        self.UI.logsink.set_location(self.ITEMS[self.TOGGLE.value])

    def handler(self, _match) -> None:
        """Handle event."""

        self.UI.logsink.set_location(self.ITEMS[self.TOGGLE.cycle])
        self.UI.show_status()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.TOGGLE.value.name

    def add_arguments_to(self, parser) -> None:
        """Add arguments for this control to `parser`."""

        arg = parser.add_argument(
            "--log-location",
            choices=[x.name for x in list(self.ENUM)],
            default="NUL",
            help="choose sort order",
        )
        parser.get_default("cli").add_default_to_help(arg)

    def command(self) -> Command:
        """Create and return `Command` object for this control."""

        return Command(
            name=self.name,
            status=self.status,
            handler=self.handler,
        )
