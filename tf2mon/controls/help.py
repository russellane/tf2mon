"""Display Help."""

from tf2mon.control import Control


class HelpControl(Control):
    """Display Help."""

    name = "HELP"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.ui.show_help()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.name
