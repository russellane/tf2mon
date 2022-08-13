"""Cycle logger `level`."""

from enum import Enum

from tf2mon.control import CycleControl
from tf2mon.toggle import Toggle


class LogLevelControl(CycleControl):
    """Cycle logger `level`."""

    name = "TOGGLE-LOG-LEVEL"
    enum = Enum(f"_e_{name}", "INFO DEBUG TRACE")
    toggle = Toggle(f"_t_{name}", enum)
    items = {
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
        self.monitor.ui.logsink.set_level(self.items[self.toggle.cycle])
        self.monitor.ui.show_status()
