"""Single step control."""

from loguru import logger

from tf2mon.control import Control


class SingleStepControl(Control):
    """Single step control."""

    name = "SINGLE-STEP"

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.admin.start_single_stepping()
        logger.info("single-step")
