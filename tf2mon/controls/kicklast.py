"""Kick last killer."""

from tf2mon.control import Control
from tf2mon.player import Player
from tf2mon.users import Users


class KickLastControl(Control):
    """Kick last killer."""

    name: str = None
    attr: str = None

    def handler(self, _match) -> None:
        Users.kick_my_last_killer(self.attr)

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
