import re

from loguru import logger

import tf2mon
from tf2mon.game import GameEvent
from tf2mon.users import Users


class GameConnectedEvent(GameEvent):

    pattern = "(?P<username>.*) connected$"

    def handler(self, match: re.Match) -> None:

        (username,) = match.groups()

        logger.log("CONNECT", Users[username])

        tf2mon.ui.notify_operator = True
        if username == tf2mon.config.get("player_name"):
            tf2mon.reset_game()
