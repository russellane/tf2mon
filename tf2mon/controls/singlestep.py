"""Enable/disable `Single-Step`."""

from loguru import logger

from tf2mon.control import Control


class SingleStepControl(Control):
    """Enable/disable `Single-Step`."""

    name = "SINGLE-STEP"

    def handler(self, _match) -> None:
        self.monitor.admin.start_single_stepping()
        logger.info("single-step")
