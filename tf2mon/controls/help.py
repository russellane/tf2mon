"""Debug flag (control `say` vs `echo`)."""

from tf2mon.command import Command
from tf2mon.control import Control


class HelpControl(Control):
    """Debug flag (control `say` vs `echo`)."""

    name = "HELP"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.ui.show_help()

    def status(self) -> str:
        """Return value formatted for display."""

        return "HELP"

    def command(self) -> Command:
        """Create and return `Command` object for this control."""

        return Command(
            name=self.name,
            status=self.status,
            handler=self.handler,
        )
