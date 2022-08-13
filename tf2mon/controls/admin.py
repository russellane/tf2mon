"""Kicks queue control."""

from tf2mon.control import Control


class ClearQueuesControl(Control):
    """Docstring."""

    name = "CLEAR-QUEUES"
    action = "tf2mon_clear_queues"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.kicks.clear()
        self.monitor.ui.refresh_kicks()
        self.monitor.spams.clear()
        self.monitor.ui.refresh_spams()


class PullControl(Control):
    """Docstring."""

    name = "PULL"
    action = "tf2mon_pull"


class PushControl(Control):
    """Docstring."""

    name = "PUSH"
    action = "tf2mon_push"
