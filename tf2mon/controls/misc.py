"""Miscelleneous controls."""

from loguru import logger

import tf2mon
import tf2mon.monitor as Monitor
from tf2mon.control import BoolControl, Control
from tf2mon.toggle import Toggle


class DebugFlagControl(BoolControl):
    """Enable/disable debug (use `ECHO` or `SAY`)."""

    name = "TOGGLE-DEBUG"
    toggle = Toggle("debug", [False, True])


class ShowDebugControl(Control):
    """Show debugging."""

    name = "SHOW-DEBUG"

    def handler(self, _match) -> None:
        Monitor.ui.show_journal("help", " Grid ".center(80, "-"))
        Monitor.ui.show_journal("help", str(Monitor.ui.grid))
        for box in Monitor.ui.grid.boxes:
            Monitor.ui.show_journal("help", Monitor.ui.grid.winyx(box))


class TauntFlagControl(BoolControl):
    """Enable/disable `Taunt` messages."""

    name = "TOGGLE-TAUNT"
    toggle = Toggle("taunt", [False, True])


class ThroeFlagControl(BoolControl):
    """Enable/disable `Throe` messages."""

    name = "TOGGLE-THROE"
    toggle = Toggle("throe", [True, False])


class ShowKDControl(BoolControl):
    """Include `Kill/Death ratio` in `User.moniker`."""

    name = "TOGGLE-KD"
    toggle = Toggle("kd", [False, True])


class ShowKillsControl(BoolControl):
    """Display kills in journal window."""

    name = "TOGGLE-SHOW-KILLS"
    toggle = Toggle("kills", [False, True])


class ShowPerksControl(Control):
    """Display perks in journal window."""

    name = "SHOW-PERKS"

    def handler(self, _match) -> None:
        Monitor.ui.show_journal("help", " Perks ".center(80, "-"))
        for user in [x for x in Monitor.users.active_users() if x.perk]:
            Monitor.ui.show_journal("help", f"{user!r:25} {user.perk}")


class JoinOtherTeamControl(Control):
    """Join Other Team."""

    name = "SWITCH-MY-TEAM"

    def handler(self, _match) -> None:
        if Monitor.toggling_enabled():
            Monitor.users.me.assign_team(Monitor.users.my.opposing_team)
            Monitor.ui.update_display()

    def status(self) -> str:
        return Monitor.users.my.team.name  # if Monitor.users.my.team else "blu"


class ClearQueuesControl(Control):
    """Clear kicks and spams queues."""

    name = "CLEAR-QUEUES"
    action = "tf2mon_clear_queues"

    def handler(self, _match) -> None:
        """Handle event."""

        tf2mon.KicksControl.clear()
        Monitor.ui.refresh_kicks()
        tf2mon.SpamsControl.clear()
        Monitor.ui.refresh_spams()


class PushControl(Control):
    """Push `steamids` from game to monitor."""

    name = "PUSH"
    action = "tf2mon_push"


class SingleStepControl(Control):
    """Start single-stepping."""

    name = "SINGLE-STEP"

    def handler(self, _match) -> None:
        Monitor.admin.start_single_stepping()
        logger.info("single-step")
