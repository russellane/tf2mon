"""Include `Kill/Death ratio` in `User.moniker`."""

from tf2mon.control import BoolControl
from tf2mon.toggle import Toggle


class ShowKDControl(BoolControl):
    """Include `Kill/Death ratio` in `User.moniker`."""

    name = "TOGGLE-KD"
    toggle = Toggle("kd", [False, True])


class ShowKillsControl(BoolControl):
    """Display kills in journal window."""

    name = "TOGGLE-SHOW-KILLS"
    toggle = Toggle("kd", [False, True])
