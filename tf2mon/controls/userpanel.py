"""Cycle contents of User Panel."""

from enum import Enum
from typing import Match

import tf2mon
from tf2mon.control import Control
from tf2mon.cycle import Cycle


class UserPanelControl(Control):
    """Cycle contents of User Panel."""

    name = "TOGGLE-USER-PANEL"
    enum = Enum("enum", "AUTO DUELS KICKS SPAMS")
    cycle = Cycle("_t_user_panel", enum)

    def handler(self, _match: Match[str] | None) -> None:
        _ = self.cycle.next
        tf2mon.ui.update_display()

    def status(self) -> str:
        return self.cycle.value.name

    @property
    def value(self) -> bool:
        return self.cycle.value
