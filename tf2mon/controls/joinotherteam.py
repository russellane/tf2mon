"""Join Other Team."""

from tf2mon.control import Control


class JoinOtherTeamControl(Control):
    """Join Other Team."""

    name = "SWITCH-MY-TEAM"

    def handler(self, _match) -> None:
        """Handle event."""

        if self.monitor.toggling_enabled:
            self.monitor.me.assign_team(self.monitor.my.opposing_team)
            self.monitor.ui.update_display()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.monitor.my.team.name  # if self.monitor.my.team else "blu"
