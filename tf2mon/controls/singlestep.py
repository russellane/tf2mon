"""Enable/disable single-stepping."""

from loguru import logger

from tf2mon.control import Control


class SingleStepControl(Control):
    """Enable/disable single-stepping."""

    name = "SINGLE-STEP"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.admin.start_single_stepping()
        logger.info("single-step")
