"""Format of logger location field."""

from enum import Enum

from tf2mon.control import Control
from tf2mon.toggle import Toggle


class LogLocationControl(Control):
    """Format of logger location field."""

    name = "TOGGLE-LOG-LOCATION"

    enum = Enum("_loc_enum", "MOD NAM THM THN FILE NUL")
    toggle = Toggle("_loc_toggle", enum)
    ITEMS = {
        enum.MOD: "{module}.{function}:{line}",
        enum.NAM: "{name}.{function}:{line}",
        enum.THM: "{thread.name}:{module}.{function}:{line}",
        enum.THN: "{thread.name}:{name}.{function}:{line}",
        enum.FILE: "{file}:{function}:{line}",
        enum.NUL: None,
    }

    #
    def start(self, value: str) -> None:
        """Set to `value`."""

        self.toggle.start(self.enum.__dict__[value])
        self.monitor.ui.logsink.set_location(self.ITEMS[self.toggle.value])

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.ui.logsink.set_location(self.ITEMS[self.toggle.cycle])
        self.monitor.ui.show_status()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.toggle.value.name

    def add_arguments_to(self, parser) -> None:
        """Add arguments for this control to `parser`."""

        arg = parser.add_argument(
            "--log-location",
            choices=[x.name for x in list(self.enum)],
            default="NUL",
            help="choose format of logger location field",
        )
        parser.get_default("cli").add_default_to_help(arg)
