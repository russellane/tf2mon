"""Display message of the day."""

from tf2mon.control import Control


class MotdControl(Control):
    """Display message of the day."""

    name = "MOTD"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.ui.show_motd()
