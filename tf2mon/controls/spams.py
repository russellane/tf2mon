"""Spams queue control."""

import tf2mon
from tf2mon.control import Control
from tf2mon.msgqueue import MsgQueue
from tf2mon.spammer import Spammer


class SpamsControl(Control, MsgQueue, Spammer):
    """Spams queue."""

    name = "spams"

    def __init__(self):
        """Message queue control."""

        super().__init__(self.name)

    def pop(self, _match=None) -> None:
        super().pop()
        tf2mon.ui.refresh_spams()

    def clear(self, _match=None) -> None:
        super().clear()
        tf2mon.ui.refresh_spams()

    def popleft(self, _match=None) -> None:
        super().popleft()
        tf2mon.ui.refresh_spams()
