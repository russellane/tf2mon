"""Single-step controls."""

import re
import threading
from typing import Callable, Optional

from loguru import logger

import tf2mon
from tf2mon.control import Control


class SingleStepControl(Control):
    """Single-step control."""

    is_stepping: bool = None
    pattern: re.Pattern = None
    clear: Callable[[None], None] = None
    set: Callable[[None], None] = None
    wait: Callable[[Optional[float]], bool] = None
    _event: threading.Event = None

    def start(self) -> None:
        self._event = threading.Event()
        self.clear = self._event.clear
        self.set = self._event.set
        self.wait = self._event.wait

        if tf2mon.options.breakpoint is not None:
            self.set_single_step_lineno(tf2mon.options.breakpoint)

        if pattern := tf2mon.options.search:
            if pattern.startswith("/"):
                pattern = pattern[1:]
            self.set_single_step_pattern(pattern)

        if tf2mon.options.single_step:
            self.start_single_stepping()
        else:
            self.stop_single_stepping()

    def start_single_stepping(self):
        self.is_stepping = True
        self._event.clear()

    def stop_single_stepping(self):
        self.is_stepping = False
        self._event.set()

    def set_single_step_lineno(self, lineno=0):
        """Begin single-stepping at `lineno` if given else at eof."""

        if lineno:
            tf2mon.conlog.inject_cmd(lineno, "SINGLE-STEP")
        else:
            # stop single-stepping until eof, then single-step again
            self.stop_single_stepping()

    def set_single_step_pattern(self, pattern=None):
        """Begin single-stepping at next line that matches `pattern`.

        Pass `None` to clear the pattern.
        """

        if not pattern:
            self.pattern = None
            logger.log("ADMIN", "clear pattern")
        else:
            flags = 0
            if pattern.endswith("/i"):
                pattern = pattern[:-2]
                flags = re.IGNORECASE
            elif pattern.endswith("/"):
                pattern = pattern[:-1]
            self.pattern = re.compile(pattern, flags)
            logger.log("ADMIN", f"set search={self.pattern}")

    def step(self, line: str) -> None:
        """Involve operator if `line` requires single-step attention.

        Called by the game thread (not the admin thread) for each line read
        from conlog, to wait for the operator (when necessary) before
        processing the line.

        If there's an active single-step pattern and last `line` read from
        con_logfile matches pattern, or if we are single-stepping, then
        wait for admin thread to release the lock.

        Args:
            line: last string read from con_logfile.

        Returns:
            immediately if gate is clear, else waits for it.
        """

        # start single stepping if pattern match
        if not self.is_stepping and self.pattern and self.pattern.search(line):
            pattern = self.pattern.pattern
            flags = "i" if (self.pattern.flags & re.IGNORECASE) else ""
            logger.log("ADMIN", f"break search /{pattern}/{flags}")
            self.start_single_stepping()

        level = "nextline" if self.is_stepping else "logline"
        logger.log(level, "-" * 80)
        logger.log(level, tf2mon.conlog.last_line)

        # check gate
        self.wait()
        if self.is_stepping:
            self.clear()


class SingleStepStartControl(Control):
    """Start single-stepping."""

    name = "SINGLE-STEP"

    def handler(self, _match) -> None:
        tf2mon.SingleStepControl.start_single_stepping()
        logger.info("single-step")
