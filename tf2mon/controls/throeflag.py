"""ThroeFlag control."""

from tf2mon.command import Command
from tf2mon.control import Control
from tf2mon.toggle import Toggle


class ThroeFlagControl(Control):
    """ThroeFlag control."""

    name = "TOGGLE-THROE"

    TOGGLE = Toggle("_throe_toggle", [True, False])

    def handler(self, _match) -> None:
        """Handle event."""

        if self.monitor.toggling_enabled:
            _ = self.TOGGLE.toggle
            self.monitor.ui.show_status()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.status_on_off("throe", self.TOGGLE.value)

    @property
    def value(self) -> bool:
        """Return value."""

        return self.TOGGLE.value

    def command(self) -> Command:
        """Create and return `Command` object for this control."""

        return Command(
            name=self.name,
            status=self.status,
            handler=self.handler,
        )