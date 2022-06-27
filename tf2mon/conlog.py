"""TF2's console logfile."""

import re
import time
from collections import namedtuple
from pathlib import Path

from loguru import logger

import tf2mon


class Conlog:
    """TF2 writes console output to the file named in its `con_logfile` variable.

    Options from our command line, and commands from our admin console, may
    "inject" lines into the data stream read from the game console logfile.
    """

    # pylint: disable=too-many-instance-attributes

    _CMD = namedtuple("_cmd", ["lineno", "cmd"])

    def __init__(
        self,
        path: Path | str,
        *,
        rewind: bool = True,
        follow: bool = False,
        inject_cmds=None,
        inject_file=None,
    ):
        """Prepare to open and read the console logfile."""

        self.path = path
        self.rewind = rewind
        self.follow = follow

        self.is_eof: bool = False
        self.last_line = None
        self.lineno: int = 0
        self.re_exclude = re.compile("|".join(self._exclude_lines()))

        self._buffer: str = None
        self._file = None
        self._inject_cmds = []  # list(_CMD)
        self._is_inject_paused = False
        self._is_inject_sorted = False

        if inject_cmds:
            self._inject_cmd_list(inject_cmds)

        if inject_file:
            logger.info(f"Reading `{inject_file}`")
            with open(inject_file, encoding="utf-8") as file:
                self._inject_cmd_list(file)

    def _inject_cmd_list(self, cmds):
        """Inject list of commands into logfile."""

        for line in cmds:
            lineno, cmd = line.strip().split(":", maxsplit=1)
            self.inject_cmd(lineno, cmd)

    def inject_cmd(self, lineno, cmd):
        """Inject command into logfile before `lineno`."""

        if not cmd.startswith(tf2mon.APPTAG):
            cmd = tf2mon.APPTAG + cmd

        self._inject_cmds.append(self._CMD(int(lineno) - 1, cmd))
        self._is_inject_sorted = False

    def open(self):
        """Wait for existence of and open console logfile."""

        while not self.path.exists():
            logger.warning(f"Waiting for {str(self.path)!r}...")
            time.sleep(3)

        logger.info(f"Reading `{self.path}`")

        self._file = open(  # pylint: disable=consider-using-with
            self.path, encoding="utf-8", errors="replace"
        )

        if not self.rewind:
            while self._file.readline() != "":
                self.lineno += 1

            logger.log("ADMIN", f"lineno={self.lineno}")
            self.is_eof = True

    def readline(self):
        """Read and return next line from console lofgile.

        Return None on end-of-file, else line.strip() (which may evaluate False).
        """

        while True:

            if _buffer := self._buffer:
                self._buffer = None
                self.last_line = "{self.lineno}: {_buffer}"
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
                self.last_line = "{self.lineno + 1}: {line}"
                logger.log("injected", self.last_line)
                return line

            self.lineno += 1
            self._is_inject_paused = False

            try:
                line = self._file.readline()
            except UnicodeDecodeError as err:
                logger.critical(err)
                continue

            if line:
                line = line.strip()
                if line.startswith(tf2mon.APPTAG) and " " in line:
                    # sometimes newlines get dropped and lines are combined
                    cmd, self._buffer = line.split(sep=" ", maxsplit=1)
                    self.last_line = f"{self.lineno}: {cmd}"
                    return cmd

                if self.re_exclude.search(line):
                    logger.log("exclude", f"{self.lineno}: {line}")
                    continue

                self.last_line = f"{self.lineno}: {line}"
                return line

            self.is_eof = True
            if not self.follow:
                return None  # eof

            time.sleep(1)  # hello

    def trunc(self):
        """Truncate console logfile."""

        with open(self.path, "w", encoding="utf-8"):
            pass

    def clean(self):
        """Print non-excluded lines to `stdout`."""

        with open(self.path, encoding="utf-8", errors="replace") as file:
            for line in [x for x in file if not self.re_exclude.search(x)]:
                print(line.rstrip("\n"))

    def _exclude_lines(self) -> [str]:
        """Return list of lines to exclude."""

        return [
            "Failed to find attachment point specified for",
            "# userid name",
            "##### CTexture::LoadTextureBitsFromFile",
            "CMaterialVar::GetVecValue: trying to get a vec value for",
            "Cannot update control point",
            "DataTable warning: tf_objective_resource: Out-of-range value",
            "EmitSound: pitch out of bounds",
            'Error: Material "models/workshop/player/items/all_class',
            "Lobby updated",
            "Missing Vgui material",
            'No such variable "',
            "Requesting texture value from var",
            "SOLID_VPHYSICS static prop with no vphysics model!",
            "SetupBones: invalid bone array size",
            "ertexlit_and_unlit_generic_bump_ps20b.vcs",
            "m_face->glyph->bitmap.width is 0 for ch:32",
            "to attach particle system",
            "to get specular",
            "unknown particle system",
        ]
