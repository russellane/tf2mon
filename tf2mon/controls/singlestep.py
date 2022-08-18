"""Enable/disable `Single-Step`."""

from loguru import logger

import tf2mon
from tf2mon.control import Control


class SingleStepControl(Control):
    """Enable/disable `Single-Step`."""

    name = "SINGLE-STEP"

    def handler(self, _match) -> None:
        tf2mon.monitor.admin.start_single_stepping()
        logger.info("single-step")
