import re

from loguru import logger

import tf2mon
from tf2mon.gameevent import GameEvent


class GameSuicideEvent(GameEvent):

    pattern = "(?P<username>.*) suicided.$"

    def handler(self, match: re.Match) -> None:

        (username,) = match.groups()

        user = tf2mon.users[username]
        logger.log("SUICIDE", user)
        user.ndeaths += 1
