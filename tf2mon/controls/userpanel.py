"""Cycle contents of User Panel."""

from enum import Enum

from tf2mon.control import Control
from tf2mon.toggle import Toggle


class UserPanelControl(Control):
    """Cycle contents of User Panel."""

    name = "TOGGLE-USER-PANEL"
    enum = Enum(f"_e_{name}", "AUTO DUELS KICKS SPAMS")
    toggle = Toggle(f"_t_{name}", enum)

    def handler(self, _match) -> None:
        if self.monitor.toggling_enabled:
            _ = self.toggle.toggle
            self.monitor.ui.update_display()

    def status(self) -> str:
        return self.toggle.value.name

    @property
    def value(self) -> bool:
        return self.toggle.value
