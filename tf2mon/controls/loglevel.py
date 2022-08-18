"""Cycle logger `level`."""

from enum import Enum

import tf2mon
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

    def start(self) -> None:
        """Set logging level based on `--verbose`."""

        tf2mon.monitor.ui.logsink.set_verbose(tf2mon.monitor.options.verbose)
        self.toggle.start(self.enum.__dict__[tf2mon.monitor.ui.logsink.level])

    def handler(self, _match) -> None:
        tf2mon.monitor.ui.logsink.set_level(self.items[self.toggle.cycle])
        tf2mon.monitor.ui.show_status()
