"""Communication mechanism to "send" data to the game."""

from collections import deque

from loguru import logger


class MsgQueue:
    """Communication mechanism to "send" data to the game."""

    def __init__(self, monitor, name):
        """Create new `MsgQueue`.

        Args:
            monitor: the monitor.
            name:   name of message queue.
        """

        self.monitor = monitor
        self.name = name
        self.msgs = deque()

    def push(self, msg):
        """Append message to end of queue."""

        self.msgs.append(msg)
        logger.opt(depth=1).log("PUSH", msg)

    def pushleft(self, msg):
        """Append message to other end of queue."""

        self.msgs.insert(0, msg)
        logger.opt(depth=1).log("PUSHLEFT", msg)

    def pop(self):
        """Remove and return message from end of queue."""

        self._pop("POP", self.msgs.pop() if self.msgs else None)

    def popleft(self):
        """Remove and return message from other end of queue."""

        self._pop("POPLEFT", self.msgs.popleft() if self.msgs else None)

    def _pop(self, action, msg):

        if not self.msgs:
            logger.log("EMPTY", f" {self.name} ".center(80, "-"))
        else:
            logger.opt(depth=1).log(action, msg)

    def clear(self):
        """Remove all messages from the queue."""

        self.msgs.clear()
        logger.opt(depth=1).log("CLEAR", self.name)

    def aliases(self):
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
            last_ack = f" ; echo {self.monitor.cmd_prefix}{self.name.upper()}-POP"
            first_ack = last_ack + "LEFT"
        else:
            _echo = "say" if self.monitor.ui.debug_flag.value else "echo"
            last = first = f"{_echo} the {self.name} queue is empty."
            last_ack = first_ack = ""

        return [
            f'alias _tf2mon_{self.name}_pop "{last}{last_ack}"',
            f'alias _tf2mon_{self.name}_popleft "{first}{first_ack}"',
        ]


class MsgQueueManager:
    """Collection of `MsgQueue`s."""

    def __init__(self, monitor, path):
        """Initialize collection of `MsgQueue`s."""

        self.monitor = monitor

        # pylint: disable=consider-using-with
        self._file = open(path, "w", encoding="utf-8")

        # list(MsgQueue)
        self._queues = []

    def addq(self, name):
        """Create `MsgQueue` with `name`, add to collection and return it."""

        queue = MsgQueue(self.monitor, name)
        self._queues.append(queue)
        return queue

    def clear(self):
        """Clear all message queues."""

        for queue in self._queues:
            queue.clear()

    def send(self):
        """Send data to tf2 by writing aliases to an `exec` script."""

        self._file.seek(0)
        self._file.truncate()
        for queue in self._queues:
            print("\n".join(queue.aliases()), file=self._file)
        self._file.flush()
