"""Logging level."""

from enum import Enum

from tf2mon.control import Control
from tf2mon.toggle import Toggle


class LogLevelControl(Control):
    """Logging level."""

    name = "TOGGLE-LOG-LEVEL"

    enum = Enum("_lvl_enum", "INFO DEBUG TRACE")
    toggle = Toggle("_lvl_toggle", enum)
    ITEMS = {
        enum.INFO: "INFO",  # ""
        enum.DEBUG: "DEBUG",  # "-v"
        enum.TRACE: "TRACE",  # "-vv"
    }

    #
    def start(self, verbose: int) -> None:
        """Set logging level based on `--verbose`."""

        self.monitor.ui.logsink.set_verbose(verbose)
        self.toggle.start(self.enum.__dict__[self.monitor.ui.logsink.level])

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.ui.logsink.set_level(self.ITEMS[self.toggle.cycle])
        self.monitor.ui.show_status()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.toggle.value.name
