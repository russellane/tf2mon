"""Display Message of the Day."""

from tf2mon.control import Control


class MotdControl(Control):
    """Display Message of the Day."""

    name = "MOTD"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.ui.show_motd()
