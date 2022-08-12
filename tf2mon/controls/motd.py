"""Motd."""

from tf2mon.control import Control


class MotdControl(Control):
    """Motd."""

    name = "MOTD"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.ui.show_motd()
