"""Motd."""

from tf2mon.command import Command
from tf2mon.control import Control


class MotdControl(Control):
    """Motd."""

    name = "MOTD"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.ui.show_motd()

    def command(self) -> Command:
        """Create and return `Command` object for this control."""

        return Command(
            name=self.name,
            handler=self.handler,
        )
