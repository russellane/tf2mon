"""Kicks queue control."""

import tf2mon
from tf2mon.control import Control
from tf2mon.msgqueue import MsgQueue


class KicksControl(Control, MsgQueue):
    """Kicks queue control."""

    name = "kicks"

    def __init__(self):
        """Kicks queue control."""

        super().__init__(self.name)


class KicksPopControl(Control):
    """Pop last/latest kicks queue message."""

    name = "KICKS-POP"
    action = "tf2mon_kicks_pop"

    def handler(self, _match) -> None:
        tf2mon.controls["KicksControl"].pop()
        tf2mon.ui.refresh_kicks()


class KicksClearControl(Control):
    """Clear kicks queue."""

    name = "KICKS-CLEAR"
    action = "tf2mon_kicks_clear"

    def handler(self, _match) -> None:
        tf2mon.controls["KicksControl"].clear()
        tf2mon.ui.refresh_kicks()


class KicksPopleftControl(Control):
    """Pop first/oldest kicks queue message."""

    name = "KICKS-POPLEFT"
    action = "tf2mon_kicks_popleft"

    def handler(self, _match) -> None:
        tf2mon.controls["KicksControl"].popleft()
        tf2mon.ui.refresh_kicks()
