"""Miscelleneous controls."""

from loguru import logger

import tf2mon
from tf2mon.control import BoolControl, Control
from tf2mon.toggle import Toggle


class HelpControl(Control):
    """Display Help."""

    name = "HELP"

    def handler(self, _match) -> None:
        tf2mon.monitor.ui.show_help()

    def status(self) -> str:
        return self.name


class MotdControl(Control):
    """Display Message of the Day."""

    name = "MOTD"

    def handler(self, _match) -> None:
        tf2mon.monitor.ui.show_motd()


class DebugFlagControl(BoolControl):
    """Enable/disable debug (use `ECHO` or `SAY`)."""

    name = "TOGGLE-DEBUG"
    toggle = Toggle("debug", [False, True])


class ShowDebugControl(Control):
    """Show debugging."""

    name = "SHOW-DEBUG"

    def handler(self, _match) -> None:
        tf2mon.monitor.ui.show_debug()


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


class JoinOtherTeamControl(Control):
    """Join Other Team."""

    name = "SWITCH-MY-TEAM"

    def handler(self, _match) -> None:
        if tf2mon.monitor.toggling_enabled:
            tf2mon.monitor.me.assign_team(tf2mon.monitor.my.opposing_team)
            tf2mon.monitor.ui.update_display()

    def status(self) -> str:
        return tf2mon.monitor.my.team.name  # if tf2mon.monitor.my.team else "blu"


class ClearQueuesControl(Control):
    """Clear kicks and spams queues."""

    name = "CLEAR-QUEUES"
    action = "tf2mon_clear_queues"

    def handler(self, _match) -> None:
        """Handle event."""

        tf2mon.monitor.kicks.clear()
        tf2mon.monitor.ui.refresh_kicks()
        tf2mon.monitor.spams.clear()
        tf2mon.monitor.ui.refresh_spams()


class PushControl(Control):
    """Push `steamids` from game to monitor."""

    name = "PUSH"
    action = "tf2mon_push"


class SingleStepControl(Control):
    """Start single-stepping."""

    name = "SINGLE-STEP"

    def handler(self, _match) -> None:
        tf2mon.monitor.admin.start_single_stepping()
        logger.info("single-step")
