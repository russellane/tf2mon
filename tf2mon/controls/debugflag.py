"""Debug flag (control `say` vs `echo`)."""

from tf2mon.control import BoolControl
from tf2mon.toggle import Toggle


class DebugFlagControl(BoolControl):
    """Debug flag (control `say` vs `echo`)."""

    name = "TOGGLE-DEBUG"
    toggle = Toggle("debug", [False, True])
