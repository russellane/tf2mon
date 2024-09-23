"""Single-step controls."""

import re
import threading
from typing import Callable, Match, Pattern

from loguru import logger

import tf2mon
from tf2mon.control import Control


class SingleStepControl(Control):
    """Single-step control."""

    is_stepping: bool = False
    pattern: Pattern[str] | None = None
    clear: Callable[[], None] | None = None
    set: Callable[[], None] | None = None
    wait: Callable[[float | None], bool] | None = None
    _event: threading.Event | None = None

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

    def start_single_stepping(self) -> None:
        self.is_stepping = True
        assert self._event
        self._event.clear()

    def stop_single_stepping(self) -> None:
        self.is_stepping = False
        assert self._event
        self._event.set()

    def set_single_step_lineno(self, lineno: int = 0) -> None:
        """Begin single-stepping at `lineno` if given else at eof."""

        if lineno:
            assert tf2mon.conlog
            tf2mon.conlog.inject_cmd(lineno, "SINGLE-STEP")
        else:
            # stop single-stepping until eof, then single-step again
            self.stop_single_stepping()

    def set_single_step_pattern(self, pattern: str | None = None) -> None:
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


class SingleStepStartControl(Control):
    """Start single-stepping."""

    name = "SINGLE-STEP"

    def handler(self, _match: Match[str] | None) -> None:
        tf2mon.SingleStepControl.start_single_stepping()
        logger.info("single-step")
