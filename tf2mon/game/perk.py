import re

import tf2mon
import tf2mon.monitor as Monitor
from tf2mon.game import GameEvent


class GamePerkOnEvent(GameEvent):

    pattern = (
        r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*) rolled [0-9A-F]{6}(?P<perk>.*)"
    )

    def handler(self, match: re.Match) -> None:

        _leader, username, perk = match.groups()
        user = Monitor.users[username]
        user.perk = perk
        user.dirty = True
        tf2mon.logger.log("PERK-ON", f"{user} {perk!r}")


class GamePerkOff1Event(GameEvent):

    pattern = r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*)\'s perk has worn off."

    def handler(self, match: re.Match) -> None:

        _leader, username = match.groups()
        user = Monitor.users[username]
        user.perk = None
        user.dirty = True
        tf2mon.logger.log("PERK-OFF", f"{user} {user.perk!r}")


class GamePerkOff2Event(GameEvent):

    pattern = r"[0-9A-F]{6}\[RTD\] Your perk has worn off."

    def handler(self, match: re.Match) -> None:

        user = Monitor.users.me
        user.perk = None
        user.dirty = True
        tf2mon.logger.log("PERK-OFF", f"{user} {user.perk!r}")


class GamePerkChangeEvent(GameEvent):

    pattern = r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*) has changed class during their roll."

    def handler(self, match: re.Match) -> None:

        _leader, username = match.groups()
        user = Monitor.users[username]
        tf2mon.logger.debug(f"{user} changed class")
