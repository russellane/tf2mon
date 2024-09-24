"""Cycle scoreboard Sort column."""

from argparse import ArgumentParser
from enum import Enum
from typing import Match

import tf2mon
from tf2mon.control import CycleControl
from tf2mon.cycle import Cycle


class SortOrderControl(CycleControl):
    """Cycle scoreboard Sort column."""

    name = "TOGGLE-SORT"
    enum = Enum("enum", "AGE STEAMID CONN K KD USERNAME")
    cycle = Cycle("_t_soc", enum)
    items = {
        enum.AGE: lambda user: (user.age, user.username_upper),
        enum.STEAMID: lambda user: (user.steamid.id if user.steamid else 0, user.username_upper),
        enum.K: lambda user: (-user.nkills, user.username_upper),
        enum.KD: lambda user: (-user.kdratio, -user.nkills, user.username_upper),
        enum.CONN: lambda user: (user.elapsed, user.username_upper),
        enum.USERNAME: lambda user: user.username_upper,
    }

    def start(self) -> None:
        self.cycle.start(self.enum.__dict__[tf2mon.options.sort_order])
        tf2mon.ui.scoreboard.set_sort_order(self.cycle.value.name)
        assert self.cycle.value.name == tf2mon.options.sort_order

    def handler(self, _match: Match[str] | None) -> None:
        _ = self.cycle.next
        tf2mon.ui.scoreboard.set_sort_order(self.cycle.value.name)
        tf2mon.ui.update_display()

    def add_arguments_to(self, parser: ArgumentParser) -> None:
        arg = parser.add_argument(
            "--sort-order",
            choices=[x.name for x in list(self.enum)],
            default="KD",
            help="choose sort order",
        )
        self.add_fkey_to_help(arg)
        self.cli.add_default_to_help(arg)
