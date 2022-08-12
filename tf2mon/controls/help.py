"""Debug flag (control `say` vs `echo`)."""

from tf2mon.control import Control


class HelpControl(Control):
    """Debug flag (control `say` vs `echo`)."""

    name = "HELP"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.ui.show_help()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.name
