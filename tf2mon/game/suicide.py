import re

from loguru import logger

from tf2mon.gameevent import GameEvent
from tf2mon.users import Users


class GameSuicideEvent(GameEvent):

    pattern = "(?P<username>.*) suicided.$"

    def handler(self, match: re.Match) -> None:

        (username,) = match.groups()

        user = Users[username]
        logger.log("SUICIDE", user)
        user.ndeaths += 1
