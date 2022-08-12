"""User panel contents control."""

from enum import Enum

from tf2mon.command import Command
from tf2mon.control import Control
from tf2mon.toggle import Toggle


class UserPanelControl(Control):
    """User panel contents control."""

    name = "TOGGLE-USER-PANEL"

    ENUM = Enum("_user_panel_enum", "AUTO DUELS KICKS SPAMS")
    TOGGLE = Toggle("_user_panel_toggle", ENUM)

    def handler(self, _match) -> None:
        """Handle event."""

        if self.monitor.toggling_enabled:
            _ = self.TOGGLE.toggle
            self.monitor.ui.update_display()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.TOGGLE.value.name

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
