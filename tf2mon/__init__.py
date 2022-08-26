"""Team Fortress 2 Console Monitor."""

from loguru import logger  # noqa

APPNAME = "TF2MON"
APPTAG = APPNAME + "-"
# pylint: disable=invalid-name
config = None  # dict
monitor = None  # tf2mon.Monitor
controls: dict  # tf2mon.Controls
options = None  # argparse.Namespace
ui = None  # tf2mon.UI
