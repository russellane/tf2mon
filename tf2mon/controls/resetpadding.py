"""Reset padding."""

from loguru import logger

from tf2mon.control import Control


class ResetPaddingControl(Control):
    """Reset padding."""

    name = "RESET-PADDING"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.ui.logsink.reset_padding()
        logger.info("padding reset")
