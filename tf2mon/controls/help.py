"""Miscelleneous controls."""

import textwrap

import tf2mon
import tf2mon.monitor as Monitor
from tf2mon.control import Control


class HelpControl(Control):
    """Display Help."""

    name = "HELP"

    def handler(self, _match) -> None:

        Monitor.ui.show_journal("help", " Function Keys ".center(80, "-"))
        for line in tf2mon.controls.fkey_help().splitlines():
            Monitor.ui.show_journal("help", line)

        Monitor.ui.show_journal("help", " Admin Commands ".center(80, "-"))
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
            Monitor.ui.show_journal("help", line)

    def status(self) -> str:
        return self.name


class MotdControl(Control):
    """Display Message of the Day."""

    name = "MOTD"

    def handler(self, _match) -> None:
        motd = Monitor.tf2_scripts_dir.parent / "motd.txt"
        Monitor.ui.show_journal("help", f" {motd} ".center(80, "-"))

        with open(motd, encoding="utf-8") as file:
            for line in file:
                Monitor.ui.show_journal("help", line.strip())
