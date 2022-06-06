"""Extend `list` with a `toggle` method to cycle through the values with each access."""


class Cycle(list):
    """Circular list to return next item with each access.

    Extend `list` with a `toggle` method to cycle through the values with
    each access.
    """

    def __init__(self, name, values):
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

    def __setitem__(self, index, value):
        # ignore index
        if value not in self._values:
            raise KeyError(f"value {value!r} not in {self.name!r}")
        while self._values[self._idx] != value:
            self.next  # pylint: disable=pointless-statement
        return value

    def start(self, value):
        """Set starting `value`."""
        return self.__setitem__(None, value)  # noqa

    def __getitem__(self, index):
        return self._values[index]

    def __repr__(self):
        return str(self._values)

    @property
    def prev(self):
        """Return previous value."""
        if self._max:
            self._idx = self._max if self._idx == 0 else self._idx - 1
        return self._values[self._idx]

    @property
    def next(self):
        """Return next value."""
        if self._max:
            self._idx = 0 if self._idx == self._max else self._idx + 1
        return self._values[self._idx]

    cycle = next
    toggle = next

    @property
    def value(self):
        """Return current value."""
        return self._values[self._idx]


#    @value.setter
#    def value(self, value):
#        if value not in self._values:
#            raise KeyError(f'bad value {value!r}')
#        while self._values[self._idx] != value:
#            self.next

Toggle = Cycle
