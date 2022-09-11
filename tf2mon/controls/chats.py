"""Chats controls."""

import tf2mon.monitor as Monitor
from tf2mon.control import Control


class ClearChatsControl(Control):
    """Clear chat window(s)."""

    name = "CLEAR-CHATS"

    def handler(self, _match) -> None:
        Monitor.chats = []
        Monitor.ui.refresh_chats()
        Monitor.ui.update_display()


class RefreshChatsControl(Control):
    """Refresh chat window(s)."""

    name = "REFRESH-CHATS"

    def handler(self, _match) -> None:
        Monitor.ui.refresh_chats()
        Monitor.ui.update_display()
