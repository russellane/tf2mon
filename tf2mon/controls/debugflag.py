"""Toggle Debug (use `ECHO` or `SAY`)."""

from tf2mon.control import BoolControl
from tf2mon.toggle import Toggle


class DebugFlagControl(BoolControl):
    """Enable/disable debug (use `ECHO` or `SAY`)."""

    name = "TOGGLE-DEBUG"
    toggle = Toggle("debug", [False, True])
