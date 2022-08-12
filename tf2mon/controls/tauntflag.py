"""TauntFlag control."""

from tf2mon.control import BoolControl
from tf2mon.toggle import Toggle


class TauntFlagControl(BoolControl):
    """TauntFlag control."""

    name = "TOGGLE-TAUNT"
    toggle = Toggle("taunt", [False, True])
