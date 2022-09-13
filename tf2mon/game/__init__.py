import re

from tf2mon.regex import Regex


class GameEvent:
    """Base class of all game events."""

    pattern: str

    @property
    def regex(self) -> Regex:
        return Regex(self.pattern, self.handler)

    def handler(self, match: re.Match) -> None:
        raise NotImplementedError
