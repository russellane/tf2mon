"""ThroeFlag control."""

from tf2mon.control import BoolControl
from tf2mon.toggle import Toggle


class ThroeFlagControl(BoolControl):
    """ThroeFlag control."""

    name = "TOGGLE-THROE"
    toggle = Toggle("throe", [True, False])
