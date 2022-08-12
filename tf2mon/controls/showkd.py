"""Include kd-ratio in messages (`User.moniker`)."""

from tf2mon.control import BoolControl
from tf2mon.toggle import Toggle


class ShowKDControl(BoolControl):
    """Include kd-ratio in messages (`User.moniker`)."""

    name = "TOGGLE-KD"
    toggle = Toggle("kd", [False, True])
