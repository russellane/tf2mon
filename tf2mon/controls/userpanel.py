"""User panel contents control."""

from enum import Enum

from tf2mon.control import Control
from tf2mon.toggle import Toggle


class UserPanelControl(Control):
    """User panel contents control."""

    name = "TOGGLE-USER-PANEL"
    enum = Enum("_user_panel_enum", "AUTO DUELS KICKS SPAMS")
    toggle = Toggle("_user_panel_toggle", enum)

    def handler(self, _match) -> None:
        """Handle event."""

        if self.monitor.toggling_enabled:
            _ = self.toggle.toggle
            self.monitor.ui.update_display()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.toggle.value.name

    @property
    def value(self) -> bool:
        """Return value."""

        return self.toggle.value
