"""TF2's console logfile."""

import re
import time
from collections import namedtuple

from loguru import logger


class Conlog:
    """TF2 writes console output to the file named in its `con_logfile` variable.

    Options from our command line, and commands from our admin console, may
    "inject" lines into the data stream read from the game console logfile.
    """

    # pylint: disable=too-many-instance-attributes

    _cmd = namedtuple("_cmd", ["lineno", "cmd"])

    def __init__(self, monitor) -> None:
        """Prepare to open and read the console logfile."""

        self.monitor = monitor
        self.lineno = 0
        self.is_eof = False

        self._inject_cmds = []  # list(_cmd)
        self._is_inject_sorted = False
        self._is_inject_paused = False
        self._fp = None

        #
        self.last_line = None
        self._fmt_last_line = "{lineno}: {line}"

        # ignore lines that contain these strings
        self._excludes_re = re.compile(
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

        while not self.monitor.options.con_logfile.exists():
            logger.warning(f"waiting for {str(self.monitor.options.con_logfile)!r}...")
            time.sleep(3)

        logger.info(f"Reading `{self.monitor.options.con_logfile}`")

        self._fp = open(  # pylint: disable=consider-using-with
            self.monitor.options.con_logfile, encoding="utf-8", errors="replace"
        )

        if not self.monitor.options.rewind:
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

        if not cmd.startswith(self.monitor.cmd_prefix):
            cmd = self.monitor.cmd_prefix + cmd

        self._inject_cmds.append(self._cmd(int(lineno) - 1, cmd))
        self._is_inject_sorted = False

    def readline(self):
        """Read and return next line from console lofgile.

        Return None on end-of-file, else line.strip() (which may evaluate False).
        """

        while True:

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
                self.last_line = self._fmt_last_line.format(lineno=self.lineno + 1, line=line)
                logger.log("injected", self.last_line)
                return line

            self.lineno += 1
            self._is_inject_paused = False

            try:
                line = self._fp.readline()
            except UnicodeDecodeError as err:
                logger.critical(err)
                continue

            if line:
                line = line.strip()
                if self._excludes_re.search(line):
                    logger.log("exclude", self._fmt_last_line, lineno=self.lineno, line=line)
                    continue
                self.last_line = self._fmt_last_line.format(lineno=self.lineno, line=line)
                return line

            self.is_eof = True
            if not self.monitor.options.follow:
                return None  # eof

            time.sleep(1)  # find an alternative to polling

    def trunc(self):
        """Truncate console logfile."""

        with open(self.monitor.options.con_logfile, "w", encoding="utf-8"):
            pass

    def filter_excludes(self):
        """Return list of non-excluded lines from console logfile."""

        with open(self.monitor.options.con_logfile, encoding="utf-8", errors="replace") as file:
            for line in file:
                if not self._excludes_re.match(line):
                    yield line.strip("\n")
