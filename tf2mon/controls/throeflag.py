"""Enable/disable `Throe` messages."""

from tf2mon.control import BoolControl
from tf2mon.toggle import Toggle


class ThroeFlagControl(BoolControl):
    """Enable/disable `Throe` messages."""

    name = "TOGGLE-THROE"
    toggle = Toggle("throe", [True, False])
