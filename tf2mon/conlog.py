"""TF2 console logfile."""

import re
import time
from collections import namedtuple
from pathlib import Path

from loguru import logger

import tf2mon


class Conlog:
    """TF2 console logfile."""

    # pylint: disable=too-many-instance-attributes

    _cmd = namedtuple("_cmd", ["lineno", "cmd"])

    def __init__(self, path: Path, rewind: bool, follow: bool) -> None:
        """Prepare to open and read TF2 console logfile.

        TF2 logs messages to the file named in its `con_logfile` variable.
        """

        self.path = Path(path)
        self.rewind = rewind
        self.follow = follow
        self.lineno = 0
        self.is_eof = False

        self._inject_cmds = []  # list(_cmd)
        self._is_inject_sorted = False
        self._is_inject_paused = False
        self._buffer = None
        self._fp = None

        #
        self.last_line = None

        # ignore lines that contain these strings
        self._re_ignore = re.compile(
            "|".join(
                [
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
            )
        )

    def open(self):
        """Wait for existence of and open console logfile."""

        while not self.path.exists():
            logger.warning(f"Waiting for {str(self.path)!r}...")
            time.sleep(3)

        logger.info(f"Reading `{self.path}`")

        self._fp = open(  # pylint: disable=consider-using-with
            self.path, encoding="utf-8", errors="replace"
        )

        if not self.rewind:
            # would self._fp.seek(0, 2) but need lineno
            while self._fp.readline() != "":
                self.lineno += 1

            logger.log("ADMIN", f"lineno={self.lineno}")
            self.is_eof = True

    def inject_cmd_list(self, cmds):
        """Inject list of commands into logfile.

        Line numbers are found at the front of each command followed by a
        colon; (then the command).
        """

        if cmds:
            for line in cmds:
                lineno, cmd = line.strip().split(":", maxsplit=1)
                self.inject_cmd(lineno, cmd)

    def inject_cmd(self, lineno, cmd):
        """Inject command into logfile before `lineno`."""

        if not cmd.startswith(tf2mon.APPTAG):
            cmd = tf2mon.APPTAG + cmd

        self._inject_cmds.append(self._cmd(int(lineno) - 1, cmd))
        self._is_inject_sorted = False

    def readline(self):
        """Read and return next line from console logfile.

        Return None on end-of-file, else line.strip() (which may evaluate False).
        """

        while True:

            if _buffer := self._buffer:
                self._buffer = None
                self.last_line = "{self.lineno}: {_buffer}"
                yield _buffer
                continue

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
                yield line
                continue

            self.lineno += 1
            self._is_inject_paused = False

            try:
                line = self._fp.readline()
            except UnicodeDecodeError as err:
                logger.critical(err)
                continue

            if line:
                line = line.strip()
                if line.startswith(tf2mon.APPTAG) and " " in line:
                    # sometimes newlines get dropped and lines are combined
                    cmd, self._buffer = line.split(sep=" ", maxsplit=1)
                    self.last_line = "{self.lineno}: {cmd}"
                    yield cmd
                    continue

                self.last_line = "{self.lineno}: {line}"
                if not self._re_ignore.search(line):
                    yield line
                continue

            self.is_eof = True
            if not self.follow:
                return  # None  # eof

            time.sleep(1)  # find an alternative to polling

    def trunc(self):
        """Truncate console logfile."""

        with open(self.path, "w", encoding="utf-8"):
            pass

    def filter_excludes(self):
        """Return list of non-excluded lines from console logfile."""

        with open(self.path, encoding="utf-8", errors="replace") as file:
            for line in file:
                if not self._re_ignore.search(line):
                    yield line.strip("\n")
