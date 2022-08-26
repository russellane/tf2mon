"""Communication mechanism to "send" data to the game."""

from collections import deque
from pathlib import Path
from typing import IO

from loguru import logger

import tf2mon


class MsgQueue:
    """Communication mechanism to "send" data to the game."""

    def __init__(self, name: str):
        """Create `MsgQueue` named `name`."""

        self.name = name
        self.msgs: deque = deque()

    def push(self, msg) -> None:
        """Append message to end of queue."""

        self.msgs.append(msg)
        logger.opt(depth=1).log("PUSH", msg)

    def pushleft(self, msg) -> None:
        """Append message to other end of queue."""

        self.msgs.insert(0, msg)
        logger.opt(depth=1).log("PUSHLEFT", msg)

    def pop(self) -> None:
        """Remove and return message from end of queue."""

        if not self.msgs:
            logger.log("EMPTY", f" {self.name} ".center(80, "-"))
        else:
            logger.opt(depth=1).log("POP", self.msgs.pop())

    def popleft(self) -> None:
        """Remove and return message from other end of queue."""

        if not self.msgs:
            logger.log("EMPTY", f" {self.name} ".center(80, "-"))
        else:
            logger.opt(depth=1).log("POPLEFT", self.msgs.popleft())

    def clear(self) -> None:
        """Remove all messages from the queue."""

        self.msgs.clear()
        logger.opt(depth=1).log("CLEAR", self.name)

    def aliases(self) -> list[str]:
        """Return message queue function key aliases.

        Create and return definitions of the `_tf2mon` prefixed-
        aliases that are called from `~/tf2/cfg/tf2-monitor.cfg`.

                                                      --- these aliases ---
        alias tf2mon_kicks_pop          "tf2mon_pull; _tf2mon_kicks_pop"
        alias tf2mon_kicks_popleft      "tf2mon_pull; _tf2mon_kicks_popleft"
        alias tf2mon_spams_pop          "tf2mon_pull; _tf2mon_spams_pop"
        alias tf2mon_spams_popleft      "tf2mon_pull; _tf2mon_spams_popleft"
        """

        # Create acknowledgement commands like this:
        #
        #   echo TF2MON-KICKS-POP
        #   echo TF2MON-KICKS-POPLEFT
        #   echo TF2MON-SPAMS-POP
        #   echo TF2MON-SPAMS-POPLEFT

        if self.msgs:
            last, first = self.msgs[-1], self.msgs[0]
            last_ack = f" ; echo {tf2mon.APPTAG}{self.name.upper()}-POP"
            first_ack = last_ack + "LEFT"
        else:
            _echo = "say" if tf2mon.controls["DebugFlagControl"].value else "echo"
            last = first = f"{_echo} the {self.name} queue is empty."
            last_ack = first_ack = ""

        return [
            f'alias _tf2mon_{self.name}_pop "{last}{last_ack}"',
            f'alias _tf2mon_{self.name}_popleft "{first}{first_ack}"',
        ]


class MsgQueueManager:
    """Collection of `MsgQueue`s."""

    _queues: list[MsgQueue] = []
    _file: IO[str] | None = None

    def __init__(self, path: Path):
        """Initialize collection of `MsgQueue`s."""

        if path and path.parent.is_dir():
            # pylint: disable=consider-using-with
            self._file = open(path, "w", encoding="utf-8")  # noqa

    def addq(self, name: str) -> MsgQueue:
        """Create `MsgQueue` with `name`, add to collection and return it."""

        queue = MsgQueue(name)
        self._queues.append(queue)
        return queue

    def clear(self) -> None:
        """Clear all message queues."""

        for queue in self._queues:
            queue.clear()

    def send(self) -> None:
        """Send data to tf2 by writing aliases to an `exec` script."""

        if not self._file:
            return

        self._file.seek(0)
        self._file.truncate()
        for queue in self._queues:
            print("\n".join(queue.aliases()), file=self._file)
        self._file.flush()
