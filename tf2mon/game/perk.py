import re

from loguru import logger

from tf2mon.game import GameEvent
from tf2mon.users import Users


class GamePerkOnEvent(GameEvent):

    pattern = (
        r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*) rolled [0-9A-F]{6}(?P<perk>.*)"
    )

    def handler(self, match: re.Match) -> None:

        username, perk = match.groups()
        user = Users[username]
        user.perk = perk
        user.dirty = True
        logger.log("PERK-ON", f"{user} {perk!r}")


class GamePerkOff1Event(GameEvent):

    pattern = r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*)\'s perk has worn off."

    def handler(self, match: re.Match) -> None:

        (username,) = match.groups()
        user = Users[username]
        user.perk = None
        user.dirty = True
        logger.log("PERK-OFF", f"{user} {user.perk!r}")


class GamePerkOff2Event(GameEvent):

    pattern = r"[0-9A-F]{6}\[RTD\] Your perk has worn off."

    def handler(self, match: re.Match) -> None:

        user = Users.me
        user.perk = None
        user.dirty = True
        logger.log("PERK-OFF", f"{user} {user.perk!r}")


class GamePerkChangeEvent(GameEvent):

    pattern = r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*) has changed class during their roll."

    def handler(self, match: re.Match) -> None:

        (username,) = match.groups()
        user = Users[username]
        logger.debug(f"{user} changed class")
