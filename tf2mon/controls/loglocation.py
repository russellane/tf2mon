"""Format of logger location field."""

from enum import Enum

from tf2mon.command import Command
from tf2mon.control import Control
from tf2mon.toggle import Toggle


class LogLocationControl(Control):
    """Format of logger location field."""

    ENUM = Enum("_loc_enum", "MOD NAM THM THN FILE NUL")
    TOGGLE = Toggle("_loc_toggle", ENUM)
    ITEMS = {
        ENUM.MOD: "{module}.{function}:{line}",
        ENUM.NAM: "{name}.{function}:{line}",
        ENUM.THM: "{thread.name}:{module}.{function}:{line}",
        ENUM.THN: "{thread.name}:{name}.{function}:{line}",
        ENUM.FILE: "{file}:{function}:{line}",
        ENUM.NUL: None,
    }

    @classmethod
    def add_arguments_to(cls, parser) -> None:
        """Add arguments for this control to `parser`."""

        arg = parser.add_argument(
            "--log-location",
            choices=[x.name for x in list(cls.ENUM)],
            default="NUL",
            help="choose sort order",
        )
        parser.get_default("cli").add_default_to_help(arg)

    @classmethod
    def start(cls, value: str) -> None:
        """Set to `value`."""

        cls.TOGGLE.start(cls.ENUM.__dict__[value])
        cls.UI.logsink.set_location(cls.ITEMS[cls.TOGGLE.value])

    @classmethod
    def command(cls) -> Command:
        """Create and return `Command` object for this control."""

        return Command(
            name="TOGGLE-LOG-LOCATION",
            status=lambda: cls.TOGGLE.value.name,
            handler=lambda m: (
                cls.UI.logsink.set_location(cls.ITEMS[cls.TOGGLE.cycle]),
                cls.UI.show_status(),
            ),
        )
