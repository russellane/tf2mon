"""Chats controls."""

import tf2mon
from tf2mon.control import Control


class ClearChatsControl(Control):
    """Clear chat window(s)."""

    name = "CLEAR-CHATS"

    def handler(self, _match) -> None:
        tf2mon.monitor.chats = []
        tf2mon.ui.refresh_chats()
        tf2mon.ui.update_display()


class RefreshChatsControl(Control):
    """Refresh chat window(s)."""

    name = "REFRESH-CHATS"

    def handler(self, _match) -> None:
        tf2mon.ui.refresh_chats()
        tf2mon.ui.update_display()
