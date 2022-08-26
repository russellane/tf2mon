import re

import tf2mon
from tf2mon.regex import Regex


class GameEvent:
    """Base class of all game events."""

    leader = r"^(\d{2}/\d{2}/\d{4} - \d{2}:\d{2}:\d{2}: )?"  # anchor to head; optional timestamp

    pattern: str

    @property
    def regex(self) -> Regex:
        tf2mon.logger.debug(f"Compiling `{self.pattern}`")
        return Regex(self.leader + self.pattern, self.handler)

    def handler(self, match: re.Match) -> None:
        raise NotImplementedError
