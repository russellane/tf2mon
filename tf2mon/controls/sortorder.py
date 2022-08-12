"""Scoreboard sort-order control."""

from enum import Enum

from tf2mon.control import Control
from tf2mon.toggle import Toggle


class SortOrderControl(Control):
    """Scoreboard sort-order control."""

    name = "TOGGLE-SORT"

    enum = Enum("_so_enum", "STEAMID K KD CONN USERNAME")
    toggle = Toggle("_so_toggle", enum)
    ITEMS = {
        enum.STEAMID: lambda user: (user.steamid.id if user.steamid else 0, user.username_upper),
        enum.K: lambda user: (-user.nkills, user.username_upper),
        enum.KD: lambda user: (-user.kdratio, -user.nkills, user.username_upper),
        enum.CONN: lambda user: (user.elapsed, user.username_upper),
        enum.USERNAME: lambda user: user.username_upper,
    }

    #
    def start(self, value: str) -> None:
        """Set to `value`."""

        self.toggle.start(self.enum.__dict__[value])
        self.monitor.ui.scoreboard.set_sort_order(self.toggle.value.name)
        assert self.toggle.value.name == value

    def handler(self, _match) -> None:
        """Handle event."""

        _ = self.toggle.toggle
        self.monitor.ui.scoreboard.set_sort_order(self.toggle.value.name)
        self.monitor.ui.update_display()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.toggle.value.name

    @property
    def value(self) -> callable:
        """Return value."""

        return self.ITEMS[self.toggle.value]

    def add_arguments_to(self, parser) -> None:
        """Add arguments for this control to `parser`."""

        arg = parser.add_argument(
            "--sort-order",
            choices=[x.name for x in list(self.enum)],
            default="KD",
            help="choose sort order",
        )
        parser.get_default("cli").add_default_to_help(arg)
