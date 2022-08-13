"""Format of logger location field."""

from enum import Enum

from tf2mon.control import CycleControl
from tf2mon.toggle import Toggle


class LogLocationControl(CycleControl):
    """Format of logger location field."""

    name = "TOGGLE-LOG-LOCATION"
    enum = Enum(f"_e_{name}", "MOD NAM THM THN FILE NUL")
    toggle = Toggle(f"_t_{name}", enum)
    items = {
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
        self.monitor.ui.logsink.set_location(self.items[self.toggle.value])

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.ui.logsink.set_location(self.items[self.toggle.cycle])
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
        self.add_fkey_to_help(arg)
        self.cli.add_default_to_help(arg)
