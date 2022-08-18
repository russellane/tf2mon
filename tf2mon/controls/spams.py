"""Spams queue control."""

import tf2mon
from tf2mon.control import Control


class SpamsPopControl(Control):
    """Pop last/latest spams queue message."""

    name = "SPAMS-POP"
    action = "tf2mon_spams_pop"

    def handler(self, _match) -> None:
        tf2mon.monitor.spams.pop()
        tf2mon.monitor.ui.refresh_spams()


class SpamsClearControl(Control):
    """Clear spams queue."""

    name = "SPAMS-CLEAR"
    action = "tf2mon_spams_clear"

    def handler(self, _match) -> None:
        tf2mon.monitor.spams.clear()
        tf2mon.monitor.ui.refresh_spams()


class SpamsPopleftControl(Control):
    """Pop first/oldest spams queue message."""

    name = "SPAMS-POPLEFT"
    action = "tf2mon_spams_popleft"

    def handler(self, _match) -> None:
        tf2mon.monitor.spams.popleft()
        tf2mon.monitor.ui.refresh_spams()
