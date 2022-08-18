"""Show debugging."""

import tf2mon
from tf2mon.control import Control


class ShowDebugControl(Control):
    """Show debugging."""

    name = "SHOW-DEBUG"

    def handler(self, _match) -> None:
        tf2mon.monitor.ui.show_debug()
