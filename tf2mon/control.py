"""Application control."""

from enum import Enum

from tf2mon.command import Command
from tf2mon.toggle import Toggle


class Control:
    """Application control."""

    UI = None

    def __init__(self):
        """Application control."""


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

    @classmethod
    def add_arguments_to(cls, parser) -> None:
        """Add arguments for this control to `parser`."""

        arg = parser.add_argument(
            "--sort-order",
            choices=[x.name for x in list(cls.ENUM)],
            default="KD",
            help="choose sort order",
        )
        cli = parser.get_default("cli")
        cli.add_default_to_help(arg)

    @classmethod
    def start(cls, value: str) -> None:
        """Docstring."""

        cls.TOGGLE.start(cls.ENUM.__dict__[value])
        cls.UI.set_sort_order(cls.TOGGLE.value)

    @classmethod
    def command(cls) -> Command:
        """Return `Command` object for this control."""

        return Command(
            name="TOGGLE-SORT",
            status=lambda: cls.TOGGLE.value.name,
            handler=lambda m: (
                cls.UI.set_sort_order(cls.TOGGLE.toggle),
                cls.UI.update_display(),
            ),
        )

    @classmethod
    @property
    def key(cls) -> callable:
        """Docstring."""

        return cls.SORT_KEYS[cls.TOGGLE.value]
