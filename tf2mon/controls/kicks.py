"""Kicks queue control."""

import tf2mon
from tf2mon.control import Control
from tf2mon.msgqueue import MsgQueue


class KicksControl(Control, MsgQueue):
    """Kicks queue."""

    name = "kicks"

    def __init__(self):
        """Message queue control."""

        super().__init__(self.name)

    def pop(self, _match=None) -> None:
        super().pop()
        tf2mon.ui.refresh_kicks()

    def clear(self, _match=None) -> None:
        super().clear()
        tf2mon.ui.refresh_kicks()

    def popleft(self, _match=None) -> None:
        super().popleft()
        tf2mon.ui.refresh_kicks()
