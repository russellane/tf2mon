"""Show debugging."""

from tf2mon.control import Control


class ShowDebugControl(Control):
    """Show debugging."""

    name = "SHOW-DEBUG"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.ui.show_debug()
