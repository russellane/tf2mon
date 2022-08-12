"""Debug flag (control `say` vs `echo`)."""

from tf2mon.control import Control
from tf2mon.toggle import Toggle


class DebugFlagControl(Control):
    """Debug flag (control `say` vs `echo`)."""

    name = "TOGGLE-DEBUG"

    TOGGLE = Toggle("_df_toggle", [False, True])

    def handler(self, _match) -> None:
        """Handle event."""

        if self.monitor.toggling_enabled:
            _ = self.TOGGLE.toggle
            self.monitor.ui.show_status()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.status_on_off("debug", self.TOGGLE.value)

    @property
    def value(self) -> bool:
        """Return value."""

        return self.TOGGLE.value
