"""Spams queue control."""

import tf2mon
import tf2mon.monitor as Monitor
from tf2mon.control import Control
from tf2mon.msgqueue import MsgQueue


class SpamsControl(Control, MsgQueue):
    """Spams queue control."""

    name = "spams"

    def __init__(self):
        """Spams queue control."""

        super().__init__(self.name)


class SpamsPopControl(SpamsControl):
    """Pop last/latest spams queue message."""

    name = "SPAMS-POP"
    action = "tf2mon_spams_pop"

    def handler(self, _match) -> None:
        tf2mon.SpamsControl.pop()
        Monitor.ui.refresh_spams()


class SpamsClearControl(SpamsControl):
    """Clear spams queue."""

    name = "SPAMS-CLEAR"
    action = "tf2mon_spams_clear"

    def handler(self, _match) -> None:
        tf2mon.SpamsControl.clear()
        Monitor.ui.refresh_spams()


class SpamsPopleftControl(SpamsControl):
    """Pop first/oldest spams queue message."""

    name = "SPAMS-POPLEFT"
    action = "tf2mon_spams_popleft"

    def handler(self, _match) -> None:
        tf2mon.SpamsControl.popleft()
        Monitor.ui.refresh_spams()
