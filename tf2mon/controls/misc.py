"""Miscelleneous controls."""

from typing import Match

import tf2mon
from tf2mon.control import BoolControl, Control
from tf2mon.cycle import Cycle


class DebugFlagControl(BoolControl):
    """Enable/disable debug (use `ECHO` or `SAY`)."""

    name = "TOGGLE-DEBUG"
    cycle = Cycle("debug", [False, True])


class ShowDebugControl(Control):
    """Show debugging."""

    name = "SHOW-DEBUG"

    def handler(self, _match: Match[str] | None) -> None:
        tf2mon.ui.show_journal("help", " Grid ".center(80, "-"))
        tf2mon.ui.show_journal("help", str(tf2mon.ui.grid))
        for box in tf2mon.ui.grid.boxes:
            tf2mon.ui.show_journal("help", tf2mon.ui.grid.winyx(box))


class TauntFlagControl(BoolControl):
    """Enable/disable `Taunt` messages."""

    name = "TOGGLE-TAUNT"
    cycle = Cycle("taunt", [False, True])


class ThroeFlagControl(BoolControl):
    """Enable/disable `Throe` messages."""

    name = "TOGGLE-THROE"
    cycle = Cycle("throe", [True, False])


class ShowKDControl(BoolControl):
    """Include `Kill/Death ratio` in `User.moniker`."""

    name = "TOGGLE-KD"
    cycle = Cycle("kd", [False, True])


class ShowKillsControl(BoolControl):
    """Display kills in journal window."""

    name = "TOGGLE-SHOW-KILLS"
    cycle = Cycle("kills", [False, True])

    def handler(self, _match: Match[str] | None) -> None:
        super().handler(_match)
        tf2mon.ChatsControl.refresh()


class ShowPerksControl(Control):
    """Display perks in journal window."""

    name = "SHOW-PERKS"

    def handler(self, _match: Match[str] | None) -> None:
        tf2mon.ui.show_journal("help", " Perks ".center(80, "-"))
        for user in [x for x in tf2mon.users.active_users() if x.perk]:
            tf2mon.ui.show_journal("help", f"{user!r:25} {user.perk}")


class JoinOtherTeamControl(Control):
    """Join Other Team."""

    name = "SWITCH-MY-TEAM"

    def handler(self, _match: Match[str] | None) -> None:
        if self.toggling_enabled():
            tf2mon.users.my.team = tf2mon.users.my.opposing_team
            tf2mon.ui.update_display()

    def status(self) -> str:
        assert tf2mon.users.my.team
        return tf2mon.users.my.team.name  # if tf2mon.users.my.team else "blu"


class ClearQueuesControl(Control):
    """Clear kicks and spams queues."""

    name = "CLEAR-QUEUES"
    action = "tf2mon_clear_queues"

    def handler(self, _match: Match[str] | None) -> None:
        """Handle event."""

        tf2mon.KicksControl.clear()
        tf2mon.ui.refresh_kicks()
        tf2mon.SpamsControl.clear()
        tf2mon.ui.refresh_spams()


class PushControl(Control):
    """Push `steamids` from game to monitor."""

    name = "PUSH"
    action = "tf2mon_push"
