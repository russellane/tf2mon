"""Docstring."""

import re
from typing import Match, Pattern


class GameEvent:
    """Base class of all game events."""

    pattern: str
    start_stepping = False  # pause before handling
    _re: Pattern[str]

    def __init__(self) -> None:
        """Docstring."""

        if self.pattern:
            self._re = re.compile(self.pattern)
            self.match = self._re.match
            self.search = self._re.search
        # else:
        #     self.match = lambda _line: False
        #     self.search = lambda _line: False

    # def match(self, _line: str) -> re.Match:
    #     return None

    # def search(self, _line: str) -> re.Match:
    #     return None

    def handler(self, match: Match[str]) -> None:
        """Docstring."""

        raise NotImplementedError
