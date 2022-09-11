import re

import tf2mon
import tf2mon.monitor as Monitor
from tf2mon.game import GameEvent


class GameConnectedEvent(GameEvent):

    pattern = "(?P<username>.*) connected$"

    def handler(self, match: re.Match) -> None:

        _leader, username = match.groups()

        tf2mon.logger.log("CONNECT", Monitor.users[username])

        Monitor.ui.notify_operator = True
        if username == tf2mon.config.get("player_name"):
            Monitor.reset_game()
