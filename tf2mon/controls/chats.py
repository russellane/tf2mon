"""Chats controls."""

from typing import Match

from loguru import logger

import tf2mon
from tf2mon.chat import Chat
from tf2mon.control import Control


class ChatsControl(Control):
    """Chats control."""

    _chats: list[Chat] = []

    def append(self, chat: Chat) -> None:
        self._chats.append(chat)
        tf2mon.ui.show_chat(chat)

    def clear(self) -> None:
        self._chats = []
        self.refresh()

    def refresh(self) -> None:

        if not hasattr(tf2mon.ui, "layout"):
            return
        assert tf2mon.ui.layout

        if tf2mon.ui.layout.chatwin_blu:
            tf2mon.ui.layout.chatwin_blu.erase()
        if tf2mon.ui.layout.chatwin_red:
            tf2mon.ui.layout.chatwin_red.erase()
        for chat in self._chats:
            tf2mon.ui.show_chat(chat)
        if tf2mon.ui.layout.chatwin_blu:
            tf2mon.ui.layout.chatwin_blu.noutrefresh()
        if tf2mon.ui.layout.chatwin_red:
            tf2mon.ui.layout.chatwin_red.noutrefresh()


class ClearChatsControl(Control):
    """Clear chat window(s)."""

    name = "CLEAR-CHATS"

    def handler(self, _match: Match[str] | None = None) -> None:
        tf2mon.ChatsControl.clear()
        tf2mon.ui.update_display()
        logger.success(self.name)


class RefreshChatsControl(Control):
    """Refresh chat window(s)."""

    name = "REFRESH-CHATS"

    def handler(self, _match: Match[str] | None = None) -> None:
        tf2mon.ChatsControl.refresh()
        tf2mon.ui.update_display()
        logger.success(self.name)
