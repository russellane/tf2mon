"""TF2's console logfile."""

import re
import time
from argparse import Namespace
from typing import IO, NamedTuple

from loguru import logger

from tf2mon.pkg import APPTAG


class _CMD(NamedTuple):
    lineno: int
    cmd: str


class Conlog:
    """TF2 writes console output to the file named in its `con_logfile` variable.

    Options from our command line, and commands from our admin console, may
    "inject" lines into the data stream read from the game console logfile.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, options: Namespace):
        """Prepare to open and read the console logfile."""

        self.path = options.con_logfile.expanduser()
        self.rewind = options.rewind
        self.follow = options.follow
        self.is_eof: bool = True
        self.last_line: str | None = None
        self.lineno: int = 0

        # strip optional timestamp; value not used.
        self._re_timestamp = re.compile(r"^\d{2}/\d{2}/\d{4} - \d{2}:\d{2}:\d{2}: ")

        logger.info(f"Reading `{options.exclude_file}`")
        self.re_exclude = re.compile(
            "|".join(options.exclude_file.expanduser().read_text(encoding="utf-8").splitlines())
        )

        self._buffer: str | None = None
        self._file: IO[str] | None = None
        self._inject_cmds: list[_CMD] = []
        self._is_inject_paused = False
        self._is_inject_sorted = False

        if options.inject_cmds:
            self._inject_cmd_list(options.inject_cmds)

        if options.inject_file:
            logger.info(f"Reading `{options.inject_file}`")
            with open(options.inject_file, encoding="utf-8") as file:
                self._inject_cmd_list(file)

    def _inject_cmd_list(self, cmds: IO[str]) -> None:
        """Inject list of commands into logfile."""

        for line in cmds:
            lineno, cmd = line.strip().split(":", maxsplit=1)
            self.inject_cmd(int(lineno), cmd)

    def inject_cmd(self, lineno: int, cmd: str) -> None:
        """Inject command into logfile before `lineno`."""

        if not cmd.startswith(APPTAG):
            cmd = APPTAG + cmd

        self._inject_cmds.append(_CMD(lineno - 1, cmd))
        self._is_inject_sorted = False

    def open(self) -> None:
        """Wait for existence of and open console logfile."""

        while not self.path.exists():
            logger.warning(f"Waiting for {str(self.path)!r}...")
            time.sleep(3)

        logger.info(f"Reading `{self.path}`")

        self._file = open(self.path, encoding="utf-8", errors="replace")  # noqa

        if self.rewind:
            self.is_eof = False
        else:
            while self._file.readline() != "":
                self.lineno += 1

            logger.log("ADMIN", f"lineno={self.lineno}")
            self.is_eof = True

    def readline(self) -> str | None:
        """Read and return next line from console lofgile.

        Return None on end-of-file, else line.strip() (which may evaluate False).
        """

        assert self._file

        while True:

            if _buffer := self._buffer:
                self._buffer = None
                self.last_line = f"{self.lineno}: {_buffer}"
                return _buffer

            if not self._is_inject_sorted:
                self._inject_cmds.sort(key=lambda x: x.lineno)
                self._is_inject_sorted = True

            if (
                self._inject_cmds
                and (self.is_eof or not self._is_inject_paused)
                and self._inject_cmds[0].lineno <= self.lineno
            ):

                line = self._inject_cmds.pop(0).cmd
                self._is_inject_paused = True
                self.last_line = f"{self.lineno + 1}: {line}"
                logger.log("injected", self.last_line)
                return line

            self._is_inject_paused = False

            try:
                line = self._file.readline()
            except UnicodeDecodeError as err:
                logger.critical(err)
                continue

            if line:
                self.lineno += 1

                line = line.strip()
                if line.startswith(APPTAG) and " " in line:
                    # sometimes newlines get dropped and lines are combined
                    cmd, self._buffer = line.split(sep=" ", maxsplit=1)
                    self.last_line = f"{self.lineno}: {cmd}"
                    return cmd

                if match := self._re_timestamp.search(line):
                    line = line[match.end() :]

                if self.re_exclude.search(line):
                    logger.log("exclude", f"{self.lineno}: {line}")
                    continue

                self.last_line = f"{self.lineno}: {line}"
                return line

            self.is_eof = True
            if not self.follow:
                return None  # eof

            time.sleep(1)  # hello

    def trunc(self) -> None:
        """Truncate console logfile."""

        with open(self.path, "w", encoding="utf-8"):
            pass

    def clean(self) -> None:
        """Print non-excluded lines to `stdout`."""

        with open(self.path, encoding="utf-8", errors="replace") as file:
            for line in [x for x in file if not self.re_exclude.search(x)]:
                print(line.rstrip("\n"))
