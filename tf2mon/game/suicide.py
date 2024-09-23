from typing import Match

from loguru import logger

import tf2mon
from tf2mon.gameevent import GameEvent
from tf2mon.user import UserKey


class GameSuicideEvent(GameEvent):

    pattern = "(?P<username>.*) suicided.$"

    def handler(self, match: Match[str]) -> None:

        (username,) = match.groups()

        user = tf2mon.users[UserKey(username)]
        logger.log("SUICIDE", user)
        user.ndeaths += 1
