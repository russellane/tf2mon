"""MsgQueue control."""

from tf2mon.control import Control
from tf2mon.msgqueue import MsgQueue


class MsgQueueControl(Control):
    """MsgQueue control."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self) -> None:
        """Initialize control."""

        self.msgq = MsgQueue(self.name)
        self.msgs = self.msgq.msgs
        self.clear = self.msgq.clear
        self.pop = self.msgq.pop
        self.popleft = self.msgq.popleft
        self.push = self.msgq.push
        self.pushleft = self.msgq.pushleft
        self.aliases = self.msgq.aliases
        super().__init__()
