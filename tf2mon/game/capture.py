import re

from loguru import logger

from tf2mon.game import GameEvent
from tf2mon.users import Users


class GameCaptureEvent(GameEvent):

    pattern = r"(?P<username>.*) (?P<action>(?:captured|defended)) (?P<capture_pt>.*) for team #(?P<s_teamno>\d)$"

    def handler(self, match: re.Match) -> None:

        username, action, capture_pt, s_teamno = match.groups()

        for name in username.split(", "):  # fix: names containing commas

            user = Users[name]

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
