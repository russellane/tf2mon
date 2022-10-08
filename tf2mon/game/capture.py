import re

from loguru import logger

import tf2mon
from tf2mon.gameevent import GameEvent
from tf2mon.user import Team


class GameCaptureEvent(GameEvent):

    pattern = r"(?P<username>.*) (?P<action>(?:captured|defended)) (?P<capture_pt>.*) for team #(?P<s_teamno>\d)$"

    def handler(self, match: re.Match) -> None:

        username, action, capture_pt, s_teamno = match.groups()

        for name in username.split(", "):  # fix: names containing commas

            user = tf2mon.users[name]

            try:
                team = Team(int(s_teamno))
                if user.team and user.team != team:
                    logger.warning(f"{user} switched to team `{team.name}`")
                user.team = team
            except ValueError as err:
                logger.error(f"{err} s_teamno {s_teamno!r}")

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
