"""Spams queue control."""

from tf2mon.control import Control


class SpamsPopControl(Control):
    """Pop last/latest spams queue message."""

    name = "SPAMS-POP"
    action = "tf2mon_spams_pop"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.spams.pop()
        self.monitor.ui.refresh_spams()


class SpamsClearControl(Control):
    """Clear spams queue."""

    name = "SPAMS-CLEAR"
    action = "tf2mon_spams_clear"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.spams.clear()
        self.monitor.ui.refresh_spams()


class SpamsPopleftControl(Control):
    """Pop first/oldest spams queue message."""

    name = "SPAMS-POPLEFT"
    action = "tf2mon_spams_popleft"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.spams.popleft()
        self.monitor.ui.refresh_spams()
