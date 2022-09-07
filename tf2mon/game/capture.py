import re

import tf2mon
import tf2mon.monitor as Monitor
from tf2mon.game import GameEvent


class GameCaptureEvent(GameEvent):

    pattern = r"(?P<username>.*) (?P<action>(?:captured|defended)) (?P<capture_pt>.*) for team #(?P<s_teamno>\d)$"

    def handler(self, match: re.Match) -> None:

        _leader, username, action, capture_pt, s_teamno = match.groups()

        for name in username.split(", "):  # fix: names containing commas

            user = Monitor.users[name]

            user.assign_teamno(int(s_teamno))

            if action == "captured":
                user.ncaptures += 1
                level = "CAP"
            else:
                user.ndefenses += 1
                level = "DEF"
            user.dirty = True
            level += user.team.name

            tf2mon.logger.log(level, f"{user} {capture_pt!r}")
            user.actions.append(f"{level} {capture_pt!r}")
