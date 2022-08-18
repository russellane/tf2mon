"""Display Message of the Day."""

import tf2mon
from tf2mon.control import Control


class MotdControl(Control):
    """Display Message of the Day."""

    name = "MOTD"

    def handler(self, _match) -> None:
        tf2mon.monitor.ui.show_motd()
