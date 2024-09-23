from typing import Match

from loguru import logger

import tf2mon
from tf2mon.gameevent import GameEvent
from tf2mon.user import UserKey


class GameConnectedEvent(GameEvent):

    pattern = "(?P<username>.*) connected$"

    def handler(self, match: Match[str]) -> None:

        (username,) = match.groups()

        logger.log("CONNECT", tf2mon.users[UserKey(username)])

        tf2mon.ui.notify_operator = True
        if username == tf2mon.config.get("player_name"):
            tf2mon.reset_game()
