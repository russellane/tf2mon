"""Grid layout control."""

from enum import Enum

import tf2mon.layouts
from tf2mon.baselayout import BaseLayout
from tf2mon.control import Control
from tf2mon.toggle import Toggle


class GridLayoutControl(Control):
    """Grid layout control."""

    name = "TOGGLE-LAYOUT"

    enum = Enum("_layout_enum", "DFLT FULL TALL MRGD WIDE")
    toggle = Toggle("_layout_toggle", enum)
    ITEMS = {
        enum.DFLT: tf2mon.layouts.default.DefaultLayout,
        enum.FULL: tf2mon.layouts.full.FullLayout,
        enum.TALL: tf2mon.layouts.tall.TallLayout,
        enum.MRGD: tf2mon.layouts.tallchat.TallChatLayout,
        enum.WIDE: tf2mon.layouts.wide.WideLayout,
    }

    #
    def start(self, value: str) -> None:
        """Set to `value`."""

        self.toggle.start(self.enum.__dict__[value])
        self.monitor.ui.grid.handle_term_resized_event()

    def handler(self, _match) -> None:
        """Handle event."""

        _ = self.toggle.toggle
        self.monitor.ui.grid.handle_term_resized_event()
        self.monitor.ui.show_status()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.toggle.value.name

    @property
    def value(self) -> type[BaseLayout]:
        """Return value."""

        return self.ITEMS[self.toggle.value]

    def add_arguments_to(self, parser) -> None:
        """Add arguments for this control to `parser`."""

        arg = parser.add_argument(
            "--layout",
            choices=[x.name for x in list(self.enum)],
            default="MRGD",
            help="choose display layout",
        )
        parser.get_default("cli").add_default_to_help(arg)
