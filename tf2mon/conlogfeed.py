"""TF2 console logfile data feed."""

from queue import SimpleQueue
from threading import Event, Thread

from loguru import logger

from tf2mon.conlog import Conlog


class ConlogFeed:
    """TF2 console logfile data feed."""

    # pylint: disable=too-few-public-methods

    name = "CONLOG"

    def __init__(self, queue: SimpleQueue, conlog: Conlog, debug: bool = False):
        """Start thread to produce lines from TF2 console logfile."""

        self.queue = queue
        self.conlog = conlog
        self.debug = debug

        self.running = Event()
        self.waiting = Event()
        # self.running.set()
        self.waiting.set()

        Thread(target=self.run, name=self.name, daemon=True).start()

    def run(self) -> None:
        """Feed lines from TF2 console logfile into queue."""

        self.conlog.open()

        for line in self.conlog.readline():

            if not self.running.is_set():
                if self.debug:
                    logger.warning(f"PAUSING: line={line!r}")

                if self.debug:
                    logger.warning("self.waiting.SET")
                self.waiting.set()

                if self.debug:
                    logger.warning("self.running.WAIT")
                self.running.wait()

                if self.debug:
                    logger.warning("self.waiting.CLEAR")
                self.waiting.clear()

            if self.debug:
                logger.warning(f"FEEDING: line={line!r}")
            self.queue.put((self.name, line))
