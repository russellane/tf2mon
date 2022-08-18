"""Reset logger `padding`."""

from loguru import logger

import tf2mon
from tf2mon.control import Control


class ResetPaddingControl(Control):
    """Reset logger `padding`."""

    name = "RESET-PADDING"

    def handler(self, _match) -> None:
        tf2mon.monitor.ui.logsink.reset_padding()
        logger.info("padding reset")
