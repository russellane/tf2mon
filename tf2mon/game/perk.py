from typing import Match

from loguru import logger

import tf2mon
from tf2mon.gameevent import GameEvent
from tf2mon.user import UserKey


class GamePerkOnEvent(GameEvent):

    pattern = (
        r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*) rolled [0-9A-F]{6}(?P<perk>.*)"
    )

    def handler(self, match: Match[str]) -> None:

        username, perk = match.groups()
        user = tf2mon.users[UserKey(username)]
        user.perk = perk
        user.dirty = True
        logger.log("PERK-ON", f"{user} {perk!r}")


class GamePerkOff1Event(GameEvent):

    pattern = r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*)\'s perk has worn off."

    def handler(self, match: Match[str]) -> None:

        (username,) = match.groups()
        user = tf2mon.users[UserKey(username)]
        user.perk = ""
        user.dirty = True
        logger.log("PERK-OFF", f"{user} {user.perk!r}")


class GamePerkOff2Event(GameEvent):

    pattern = r"[0-9A-F]{6}\[RTD\] Your perk has worn off."

    def handler(self, _match: Match[str] | None) -> None:

        user = tf2mon.users.me
        user.perk = ""
        user.dirty = True
        logger.log("PERK-OFF", f"{user} {user.perk!r}")


class GamePerkChangeEvent(GameEvent):

    pattern = r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*) has changed class during their roll."

    def handler(self, match: Match[str]) -> None:

        (username,) = match.groups()
        user = tf2mon.users[UserKey(username)]
        logger.debug(f"{user} changed class")
