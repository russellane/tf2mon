"""Display Help."""

import tf2mon
from tf2mon.control import Control


class HelpControl(Control):
    """Display Help."""

    name = "HELP"

    def handler(self, _match) -> None:
        tf2mon.monitor.ui.show_help()

    def status(self) -> str:
        return self.name
