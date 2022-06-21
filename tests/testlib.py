import os
import sys

import pytest
from loguru import logger

try:
    logger.remove(0)
except ValueError:
    ...

logger.add(
    sys.stderr,
    format="{time:HH:mm:ss.SSS} {level} {function} {line} {message}",
    level="TRACE",
)

slow = pytest.mark.skipif(not os.environ.get("SLOW"), reason="slow")
