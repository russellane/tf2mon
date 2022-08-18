"""Join Other Team."""

import tf2mon
from tf2mon.control import Control


class JoinOtherTeamControl(Control):
    """Join Other Team."""

    name = "SWITCH-MY-TEAM"

    def handler(self, _match) -> None:
        if tf2mon.monitor.toggling_enabled:
            tf2mon.monitor.me.assign_team(tf2mon.monitor.my.opposing_team)
            tf2mon.monitor.ui.update_display()

    def status(self) -> str:
        return tf2mon.monitor.my.team.name  # if tf2mon.monitor.my.team else "blu"
