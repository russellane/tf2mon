"""Kicks queue control."""

import tf2mon
from tf2mon.control import Control


class KicksPopControl(Control):
    """Pop last/latest kicks queue message."""

    name = "KICKS-POP"
    action = "tf2mon_kicks_pop"

    def handler(self, _match) -> None:
        tf2mon.monitor.kicks.pop()
        tf2mon.monitor.ui.refresh_kicks()


class KicksClearControl(Control):
    """Clear kicks queue."""

    name = "KICKS-CLEAR"
    action = "tf2mon_kicks_clear"

    def handler(self, _match) -> None:
        tf2mon.monitor.kicks.clear()
        tf2mon.monitor.ui.refresh_kicks()


class KicksPopleftControl(Control):
    """Pop first/oldest kicks queue message."""

    name = "KICKS-POPLEFT"
    action = "tf2mon_kicks_popleft"

    def handler(self, _match) -> None:
        tf2mon.monitor.kicks.popleft()
        tf2mon.monitor.ui.refresh_kicks()
