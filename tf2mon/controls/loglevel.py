"""Logging level."""

from enum import Enum

from tf2mon.command import Command
from tf2mon.control import Control
from tf2mon.toggle import Toggle


class LogLevelControl(Control):
    """Logging level."""

    name = "TOGGLE-LOG-LEVEL"

    ENUM = Enum("_lvl_enum", "INFO DEBUG TRACE")
    TOGGLE = Toggle("_lvl_toggle", ENUM)
    ITEMS = {
        ENUM.INFO: "INFO",  # ""
        ENUM.DEBUG: "DEBUG",  # "-v"
        ENUM.TRACE: "TRACE",  # "-vv"
    }

    #
    def start(self, verbose: int) -> None:
        """Set logging level based on `--verbose`."""

        self.UI.logsink.set_verbose(verbose)
        self.TOGGLE.start(self.ENUM.__dict__[self.UI.logsink.level])

    def handler(self, _match) -> None:
        """Handle event."""

        self.UI.logsink.set_level(self.ITEMS[self.TOGGLE.cycle])
        self.UI.show_status()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.TOGGLE.value.name

    def add_arguments_to(self, parser) -> None:
        """Not required; keeping vim -d happy."""

    def command(self) -> Command:
        """Create and return `Command` object for this control."""

        return Command(
            name=self.name,
            status=self.status,
            handler=self.handler,
        )
