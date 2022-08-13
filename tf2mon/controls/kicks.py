"""Kicks queue control."""

from tf2mon.control import Control


class KicksControl(Control):
    """Kicks queue control."""

    name = None
    attr = None

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.kick_my_last_killer(self.attr)

class KicksPopControl(KicksControl):
    """Consume last/latest kicks queue message."""

    name = "KICKS-POP"
    action = "tf2mon_kicks_pop"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.kicks.pop()
        self.monitor.ui.refresh_kicks()


class KicksClearControl(KicksControl):
    """Consume last/latest kicks queue message."""

    name = "KICKS-CLEAR"
    action = "tf2mon_kicks_clear"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.kicks.clear()
        self.monitor.ui.refresh_kicks()


class KicksPopleftControl(KicksControl):
    """Consume last/latest kicks queue message."""

    name = "KICKS-POPLEFT"
    action = "tf2mon_kicks_popleft"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.kicks.popleft()
        self.monitor.ui.refresh_kicks()
