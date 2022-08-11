"""Reset padding."""

from loguru import logger

from tf2mon.command import Command
from tf2mon.control import Control


class ResetPaddingControl(Control):
    """Reset padding."""

    @classmethod
    def command(cls) -> Command:
        """Create and return `Command` object for this control."""

        return Command(
            name="RESET-PADDING",
            handler=lambda m: (
                cls.UI.logsink.reset_padding(),
                logger.info("padding reset"),
            ),
        )
