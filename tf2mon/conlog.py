"""TF2 console logfile."""

import re
from collections import namedtuple
from typing import TextIO

from loguru import logger

import tf2mon


class Conlog:
    """TF2 console logfile."""

    # pylint: disable=too-many-instance-attributes

    _CMD = namedtuple("_cmd", ["lineno", "cmd"])

    def __init__(self, inject_cmds=None, inject_file=None):
        """TF2 console logfile."""

        self.lineno: int = 0
        self.last_line = None
        self._buffer = None
        self._file: TextIO = None
        self.re_exclude = re.compile("|".join(self._exclude_lines()))
        self._inject_cmds = []  # list(_cmd)
        self._is_inject_paused = False
        self._is_inject_sorted = False

        # group.add_argument(
        #     "--inject-cmd",
        #     dest="inject_cmds",
        #     metavar="LINENO:CMD",
        #     action="append",
        #     help="inject `CMD` before line `LINENO`",
        # )
        if inject_cmds:
            self._inject_cmd_list(inject_cmds)

        # group.add_argument(
        #     "--inject-file",
        #     metavar="FILE",
        #     help="read list of inject commands from `FILE`",
        # )
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

    def is_open(self) -> bool:
        """Return True if the conlog has been opened."""
        return self._file is not None

    # def read_lineno_line(self) -> (int, str):
    #     """Read next line from console logfile and yield `(lineno, line)`."""

    #     for line in self.readline():
    #         yield self.lineno, line

    def process_line(self, line: str) -> None:
        """Read and yield next line from console logfile.

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
                # and (self.is_eof or not self._is_inject_paused)
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
                line = self._file.readline()
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
                if not self.re_exclude.search(line):
                    yield line
                continue

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
