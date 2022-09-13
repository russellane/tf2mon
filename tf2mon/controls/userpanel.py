"""Cycle contents of User Panel."""

from enum import Enum

import tf2mon
from tf2mon.control import Control
from tf2mon.toggle import Toggle


class UserPanelControl(Control):
    """Cycle contents of User Panel."""

    name = "TOGGLE-USER-PANEL"
    enum = Enum("_e_user_panel", "AUTO DUELS KICKS SPAMS")
    toggle = Toggle("_t_user_panel", enum)

    def handler(self, _match) -> None:
        _ = self.toggle.toggle
        tf2mon.ui.update_display()

    def status(self) -> str:
        return self.toggle.value.name

    @property
    def value(self) -> bool:
        return self.toggle.value
