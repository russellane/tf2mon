"""Miscelleneous controls."""

import textwrap
from pathlib import Path

import tf2mon
from tf2mon.control import Control


class HelpControl(Control):
    """Display Help."""

    name = "HELP"

    def handler(self, _match) -> None:

        tf2mon.ui.show_journal("help", " Function Keys ".center(80, "-"))
        for line in tf2mon.controller.fkey_help().splitlines():
            tf2mon.ui.show_journal("help", line)

        tf2mon.ui.show_journal("help", " Admin Commands ".center(80, "-"))
        for line in (
            textwrap.dedent(
                """
            Press Enter to process next line.
            Enter "b 500" to set breakpoint at line 500.
            Enter "/pattern[/i]" to set search pattern.
            Enter "/" to clear search pattern.
            Enter "c" to continue.
            Enter "quit" or press ^D to quit."
                """
            )
            .strip()
            .splitlines()
        ):
            tf2mon.ui.show_journal("help", line)

    def status(self) -> str:
        return self.name


class MotdControl(Control):
    """Display Message of the Day."""

    name = "MOTD"
    _path: Path = None

    def start(self) -> None:
        self._path = tf2mon.options.tf2_install_dir / "cfg" / "motd.txt"

    def handler(self, _match) -> None:
        tf2mon.ui.show_journal("help", f" {self._path} ".center(80, "-"))

        with open(self._path, encoding="utf-8") as file:
            for line in file:
                tf2mon.ui.show_journal("help", line.strip())
