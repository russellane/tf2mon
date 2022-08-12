"""Enable/disable `Taunt`s."""

from tf2mon.control import BoolControl
from tf2mon.toggle import Toggle


class TauntFlagControl(BoolControl):
    """Enable/disable `Taunt`s."""

    name = "TOGGLE-TAUNT"
    toggle = Toggle("taunt", [False, True])
