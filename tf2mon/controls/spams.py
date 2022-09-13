"""Spams queue control."""

import tf2mon
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
        tf2mon.ui.refresh_spams()


class SpamsClearControl(SpamsControl):
    """Clear spams queue."""

    name = "SPAMS-CLEAR"
    action = "tf2mon_spams_clear"

    def handler(self, _match) -> None:
        tf2mon.SpamsControl.clear()
        tf2mon.ui.refresh_spams()


class SpamsPopleftControl(SpamsControl):
    """Pop first/oldest spams queue message."""

    name = "SPAMS-POPLEFT"
    action = "tf2mon_spams_popleft"

    def handler(self, _match) -> None:
        tf2mon.SpamsControl.popleft()
        tf2mon.ui.refresh_spams()
