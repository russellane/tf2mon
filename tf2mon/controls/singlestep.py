"""Single step control."""

from tf2mon.command import Command
from tf2mon.control import Control


class SingleStepControl(Control):
    """Single step control."""

    name = "SINGLE-STEP"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.admin.start_single_stepping()

    def command(self) -> Command:
        """Create and return `Command` object for this control."""

        return Command(
            name=self.name,
            handler=self.handler,
        )
