"""Scoreboard sort-order control."""

from enum import Enum

from tf2mon.command import Command
from tf2mon.control import Control
from tf2mon.toggle import Toggle


class SortOrderControl(Control):
    """Scoreboard sort-order control."""

    ENUM = Enum("_so_enum", "STEAMID K KD CONN USERNAME")
    TOGGLE = Toggle("_so_toggle", ENUM)
    SORT_KEYS = {
        ENUM.STEAMID: lambda user: (user.steamid.id if user.steamid else 0, user.username_upper),
        ENUM.K: lambda user: (-user.nkills, user.username_upper),
        ENUM.KD: lambda user: (-user.kdratio, -user.nkills, user.username_upper),
        ENUM.CONN: lambda user: (user.elapsed, user.username_upper),
        ENUM.USERNAME: lambda user: user.username_upper,
    }

    def add_arguments_to(self, parser) -> None:
        """Add arguments for this control to `parser`."""

        arg = parser.add_argument(
            "--sort-order",
            choices=[x.name for x in list(self.ENUM)],
            default="KD",
            help="choose sort order",
        )
        parser.get_default("cli").add_default_to_help(arg)

    def start(self, value: str) -> None:
        """Set to `value`."""

        self.TOGGLE.start(self.ENUM.__dict__[value])
        self.UI.set_sort_order(self.TOGGLE.value)

    def command(self) -> Command:
        """Create and return `Command` object for this control."""

        return Command(
            name="TOGGLE-SORT",
            status=lambda: self.TOGGLE.value.name,
            handler=lambda m: (
                self.UI.set_sort_order(self.TOGGLE.toggle),
                self.UI.update_display(),
            ),
        )

    @property
    def key(self) -> callable:
        """Docstring."""

        return self.SORT_KEYS[self.TOGGLE.value]
