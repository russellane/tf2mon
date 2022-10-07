import re

from loguru import logger

import tf2mon
from tf2mon.gameevent import GameEvent


class GameCaptureEvent(GameEvent):

    pattern = r"(?P<username>.*) (?P<action>(?:captured|defended)) (?P<capture_pt>.*) for team #(?P<s_teamno>\d)$"

    def handler(self, match: re.Match) -> None:

        username, action, capture_pt, s_teamno = match.groups()

        for name in username.split(", "):  # fix: names containing commas

            user = tf2mon.users[name]

            user.assign_teamno(int(s_teamno))

            if action == "captured":
                user.ncaptures += 1
                level = "CAP"
            else:
                user.ndefenses += 1
                level = "DEF"
            user.dirty = True
            level += user.team.name

            logger.log(level, f"{user} {capture_pt!r}")
            user.actions.append(f"{level} {capture_pt!r}")
