"""Reset padding."""

from loguru import logger

from tf2mon.command import Command
from tf2mon.control import Control


class ResetPaddingControl(Control):
    """Reset padding."""

    name = "RESET-PADDING"

    #
    def start(self) -> None:
        """Not required; keeping vim -d happy."""

    def handler(self, _match) -> None:
        """Handle event."""

        self.UI.logsink.reset_padding()
        logger.info("padding reset")

    def status(self) -> str:
        """Not required; keeping vim -d happy."""

    def add_arguments_to(self, parser) -> None:
        """Not required; keeping vim -d happy."""

    def command(self) -> Command:
        """Create and return `Command` object for this control."""

        return Command(
            name=self.name,
            handler=self.handler,
        )
