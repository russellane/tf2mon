"""Cycle Grid Layout."""

from argparse import ArgumentParser
from enum import Enum
from typing import Match

import tf2mon
from tf2mon.control import CycleControl
from tf2mon.layouts.chat import ChatLayout
from tf2mon.layouts.default import DefaultLayout
from tf2mon.layouts.full import FullLayout
from tf2mon.layouts.tall import TallLayout
from tf2mon.layouts.tallchat import TallChatLayout
from tf2mon.layouts.wide import WideLayout
from tf2mon.toggle import Toggle


class GridLayoutControl(CycleControl):
    """Cycle grid layout."""

    name = "TOGGLE-LAYOUT"
    enum = Enum("enum", "CHAT DFLT FULL TALL MRGD WIDE")
    toggle = Toggle("_t_layout", enum)
    items = {
        enum.CHAT: ChatLayout,
        enum.DFLT: DefaultLayout,
        enum.FULL: FullLayout,
        enum.TALL: TallLayout,
        enum.MRGD: TallChatLayout,
        enum.WIDE: WideLayout,
    }

    def start(self) -> None:
        self.toggle.start(self.enum.__dict__[tf2mon.options.layout])
        tf2mon.ui.grid.handle_term_resized_event()

    def handler(self, _match: Match[str] | None) -> None:
        _ = self.toggle.toggle
        tf2mon.ui.grid.handle_term_resized_event()
        tf2mon.ui.update_display()

    def add_arguments_to(self, parser: ArgumentParser) -> None:
        arg = parser.add_argument(
            "--layout",
            choices=[x.name for x in list(self.enum)],
            default="MRGD",
            help="choose display layout",
        )
        self.add_fkey_to_help(arg)
        self.cli.add_default_to_help(arg)
