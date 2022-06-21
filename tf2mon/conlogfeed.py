"""Console Logfile Data Feed.

Tail -f the con_logfile, forwarding lines
through a SimpleQueue to the main-thread.
"""

import os
import time
from pathlib import Path
from queue import SimpleQueue
from threading import Thread

from loguru import logger


class ConlogFeed:
    """TF2 console logfile data feed."""

    # pylint: disable=too-few-public-methods

    msgtype = "CONLOG"
    lineno: int = 0
    is_eof: bool = False

    def __init__(
        self,
        queue: SimpleQueue,
        path: os.PathLike,
        rewind: bool = True,
        follow: bool = False,
    ):
        """Start thread to forward lines from con_logfile to application."""

        self.queue = queue
        self.path = Path(path)
        self.rewind = rewind
        self.follow = follow

        Thread(target=self.run, name=self.msgtype, daemon=True).start()

    def run(self) -> None:
        """Forward lines from con_logfile to application."""

        while not self.path.exists():
            logger.warning(f"Waiting for {str(self.path)!r}...")
            time.sleep(3)

        with open(self.path, encoding="utf-8", errors="replace") as file:

            if not self.rewind:
                for _ in file:
                    self.lineno += 1

            while True:
                for line in file:
                    self.lineno += 1
                    self.queue.put((self.msgtype, self.lineno, line))
                    time.sleep(0.001)  # need context switch

                self.is_eof = True
                if not self.follow:
                    self.queue.put((self.msgtype, -self.lineno, ""))
                    break
                time.sleep(1)
