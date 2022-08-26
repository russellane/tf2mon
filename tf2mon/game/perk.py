import re

import tf2mon
from tf2mon.game import GameEvent


class GamePerkEvent(GameEvent):

    pattern = "|".join(
        [
            r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*) rolled [0-9A-F]{6}(?P<perk>.*)",
            # r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*)\'s perk has worn off.",
            # r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*) has changed class during their roll.",
            # r"[0-9A-F]{6}\[RTD\] Your perk has worn off.",
        ]
    )

    def handler(self, match: re.Match) -> None:

        username, perk = match.groups()

        user = tf2mon.monitor.users[username] if username else tf2mon.monitor.me

        if perk:
            tf2mon.logger.log("PERK-ON", f"{user} {perk!r}")
        else:
            tf2mon.logger.log("PERK-OFF", f"{user} {user.perk!r}")

        user.perk = perk
        user.dirty = True
