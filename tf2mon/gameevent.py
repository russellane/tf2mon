"""Docstring."""

import re


class GameEvent:
    """Base class of all game events."""

    pattern: str = None
    start_stepping = False  # pause before handling
    _re: re.Pattern = None

    def __init__(self):
        """Docstring."""

        if self.pattern:
            self._re = re.compile(self.pattern)
            self.match = self._re.match
            self.search = self._re.search
        else:
            self.match = lambda _line: False
            self.search = lambda _line: False

    # def match(self, _line: str) -> re.Match:
    #     return None

    # def search(self, _line: str) -> re.Match:
    #     return None

    def handler(self, match: re.Match) -> None:
        """Docstring."""

        raise NotImplementedError
