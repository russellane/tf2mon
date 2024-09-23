"""Kick last killer."""

from typing import Match

import tf2mon
from tf2mon.control import Control
from tf2mon.player import Player


class KickLastControl(Control):
    """Kick last killer."""

    attr: str

    def handler(self, _match: Match[str] | None) -> None:
        tf2mon.users.kick_my_last_killer(self.attr)

    def status(self) -> str:
        return self.attr


class KickLastCheaterControl(KickLastControl):
    """Kick last killer as `cheater`."""

    name = "KICK-LAST-CHEATER"
    attr = Player.CHEATER


class KickLastRacistControl(KickLastControl):
    """Kick last killer as `racist`."""

    name = "KICK-LAST-RACIST"
    attr = Player.RACIST


class KickLastSuspectControl(KickLastControl):
    """Mark last killer as `suspect`."""

    name = "KICK-LAST-SUSPECT"
    attr = Player.SUSPECT
