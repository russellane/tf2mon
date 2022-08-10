"""Logging level."""

from enum import Enum

from tf2mon.command import Command
from tf2mon.control import Control
from tf2mon.toggle import Toggle


class LogLevelControl(Control):
    """Logging level."""

    ENUM = Enum("_lvl_enum", "INFO DEBUG TRACE")
    TOGGLE = Toggle("_lvl_toggle", ENUM)
    ITEMS = {
        ENUM.INFO: "INFO",  # ""
        ENUM.DEBUG: "DEBUG",  # "-v"
        ENUM.TRACE: "TRACE",  # "-vv"
    }

    @classmethod
    def start(cls, verbose: int) -> None:
        """Set logging level based on `--verbose`."""

        cls.UI.logsink.set_verbose(verbose)
        cls.TOGGLE.start(cls.ENUM.__dict__[cls.UI.logsink.level])

    @classmethod
    def command(cls) -> Command:
        """Create and return `Command` object for this control."""

        return Command(
            name="TOGGLE-LOG-LEVEL",
            status=lambda: cls.TOGGLE.value.name,
            handler=lambda m: (
                cls.UI.logsink.set_level(cls.ITEMS[cls.TOGGLE.cycle]),
                cls.UI.show_status(),
            ),
        )
