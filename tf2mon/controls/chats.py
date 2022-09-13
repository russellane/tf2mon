"""Chats controls."""

import tf2mon
from tf2mon.chat import Chat
from tf2mon.control import Control


class ChatsControl(Control):
    """Chats control."""

    _chats: list[Chat] = []

    def append(self, chat: Chat) -> None:
        self._chats.append(chat)

    def clear(self) -> None:
        self._chats = []

    @property
    def value(self) -> list[Chat]:
        return self._chats


class ClearChatsControl(Control):
    """Clear chat window(s)."""

    name = "CLEAR-CHATS"

    def handler(self, _match) -> None:
        tf2mon.ChatsControl.clear()
        tf2mon.ui.refresh_chats()
        tf2mon.ui.update_display()


class RefreshChatsControl(Control):
    """Refresh chat window(s)."""

    name = "REFRESH-CHATS"

    def handler(self, _match) -> None:
        tf2mon.ui.refresh_chats()
        tf2mon.ui.update_display()
