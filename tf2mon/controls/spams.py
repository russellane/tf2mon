"""Spams queue control."""

from typing import Match

import tf2mon
from tf2mon.controls.msgqueue import MsgQueueControl


class SpamsControl(MsgQueueControl):
    """Spams queue control."""

    name = "spams"


class SpamsPopControl(SpamsControl):
    """Pop last/latest spams queue message."""

    name = "SPAMS-POP"
    action = "tf2mon_spams_pop"

    def handler(self, _match: Match[str] | None) -> None:
        tf2mon.SpamsControl.pop()
        tf2mon.ui.refresh_spams()


class SpamsClearControl(SpamsControl):
    """Clear spams queue."""

    name = "SPAMS-CLEAR"
    action = "tf2mon_spams_clear"

    def handler(self, _match: Match[str] | None) -> None:
        tf2mon.SpamsControl.clear()
        tf2mon.ui.refresh_spams()


class SpamsPopleftControl(SpamsControl):
    """Pop first/oldest spams queue message."""

    name = "SPAMS-POPLEFT"
    action = "tf2mon_spams_popleft"

    def handler(self, _match: Match[str] | None) -> None:
        tf2mon.SpamsControl.popleft()
        tf2mon.ui.refresh_spams()
