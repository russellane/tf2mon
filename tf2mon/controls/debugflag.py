"""Control use of `SAY` vs `ECHO`."""

from tf2mon.control import BoolControl
from tf2mon.toggle import Toggle


class DebugFlagControl(BoolControl):
    """Control use of `SAY` vs `ECHO`."""

    name = "TOGGLE-DEBUG"
    toggle = Toggle("debug", [False, True])
