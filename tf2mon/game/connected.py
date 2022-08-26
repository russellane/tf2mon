import re

import tf2mon
from tf2mon.game import GameEvent


class GameConnectedEvent(GameEvent):

    pattern = "(?P<username>.*) connected$"

    def handler(self, match: re.Match) -> None:

        _leader, username = match.groups()

        tf2mon.logger.log("CONNECT", tf2mon.monitor.users[username])

        tf2mon.ui.notify_operator = True
        if username == tf2mon.config.get("player_name"):
            tf2mon.monitor.reset_game()
