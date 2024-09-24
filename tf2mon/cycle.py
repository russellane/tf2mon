"""Circular list that returns next item with each access."""

from typing import Any


class Cycle:
    """Circular list that returns next item with each access."""

    def __init__(self, name: str, values: Any) -> None:
        """Create new `Cycle`.

        Args:
            name:   name of instance.
            values: list of values to cycle through.
        """

        super().__init__()

        self.name = name
        assert values
        self._values = list(values)
        _len = len(self._values)
        assert _len
        self._max = _len - 1
        self._idx = 0

    def __setitem__(self, _index: int, value: Any) -> None:
        if value not in self._values:
            raise KeyError(f"value {value!r} not in {self.name!r}")
        while self._values[self._idx] != value:
            _ = self.next

    def start(self, value: Any) -> None:
        """Set starting `value`."""
        self.__setitem__(0, value)  # pylint: disable=unnecessary-dunder-call

    def __getitem__(self, index: int) -> Any:
        return self._values[index]

    def __repr__(self) -> str:
        return str(self._values)

    @property
    def prev(self) -> Any:
        """Return previous value."""
        if self._max:
            self._idx = self._max if self._idx == 0 else self._idx - 1
        return self._values[self._idx]

    @property
    def next(self) -> Any:
        """Return next value."""
        if self._max:
            self._idx = 0 if self._idx == self._max else self._idx + 1
        return self._values[self._idx]

    cycle = next

    @property
    def value(self) -> Any:
        """Return current value."""
        return self._values[self._idx]
