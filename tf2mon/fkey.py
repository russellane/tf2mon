"""Function Keys."""

import curses
import re
from typing import ClassVar

# Values for `modifier`; also used as `label` prefix.
MOD_BASE = ""
MOD_CTRL = "c"
MOD_SHIFT = "s"


class FKey:
    """The simultaneous pressing of a base key and an optional modifier key."""

    pattern: ClassVar[re.Pattern] = re.compile(r"^(?:(SHIFT|CTRL)\+)?(F)?(.+)$")

    curses_from_game: ClassVar[dict[str, int]] = {
        "KP_HOME": curses.KEY_HOME,
        "KP_END": curses.KEY_END,
        "KP_UPARROW": curses.KEY_UP,
        "KP_DOWNARROW": curses.KEY_DOWN,
        "KP_LEFTARROW": curses.KEY_LEFT,
        "KP_RIGHTARROW": curses.KEY_RIGHT,
        "KP_PGUP": curses.KEY_PPAGE,
        "KP_PGDN": curses.KEY_NPAGE,
        "KP_5": curses.KEY_B2,
        "KP_INS": curses.KEY_IC,
        "KP_DEL": curses.KEY_DC,
        # "xxx": curses.KEY_SR,
        # "xxx": curses.KEY_SF,
        # "xxx": curses.KEY_SLEFT,
        # "xxx": curses.KEY_SRIGHT,
        # "xxx": curses.KEY_SDC,  # can't do KEY_SIC
    }

    def __init__(self, keyspec: str):
        """Init `FKey` from `keyspec`.

        Keyname in TF2 terms, with optional modifier "shift+" or "ctrl+" (not both).
        e.g., "A", "shift+A", "ctrl+KP_LEFTARROW".

        Case-insensitive:
        >>> FKey("a").__dict__ == FKey("A").__dict__
        True
        >>> FKey("shift+a").__dict__ == FKey("shift+A").__dict__
        True

        Note that:
        >>> FKey("shift+a").__dict__ != FKey("A").__dict__
        True
        >>> FKey("shift+A").__dict__ != FKey("A").__dict__
        True
        """

        # pylint: disable=too-many-branches

        if not keyspec:
            raise ValueError("keyspec", keyspec)
        self.keyspec = keyspec.upper()

        matched = self.pattern.match(self.keyspec)
        if not matched:
            raise ValueError("keyspec", self.keyspec)

        mod, eff, key = matched.groups()
        self.name: str = (eff or "") + key  # TF2 terms: "B", "KP_LEFTARROW", "F1"

        self.modifier: str = MOD_BASE
        if mod:
            if mod == "SHIFT":
                self.modifier = MOD_SHIFT
            elif mod == "CTRL":
                self.modifier = MOD_CTRL
            else:
                raise ValueError("keyspec", self.keyspec)

        self.key: int = None  # ord("B"), curses.KEY_LEFT, curses.KEY_F1
        if eff:
            self.key = curses.KEY_F0
            try:
                self.key += int(key)
            except ValueError as exc:
                raise ValueError("keyspec", self.keyspec) from exc
        elif len(key) == 1:
            self.key = ord(key)
        elif (key := self.curses_from_game.get(key)) is not None:
            self.key = key
        else:
            raise ValueError("keyspec", self.keyspec)

        if eff:
            if self.modifier == MOD_SHIFT:
                self.key += 12
            elif self.modifier == MOD_CTRL:
                self.key += 24

        self.label: str = self.modifier + self.name  # display name

    def __repr__(self):
        return str(self.__dict__)

    @property
    def is_base(self) -> bool:
        """Return True if only `base` key was pressed."""
        return self.modifier == MOD_BASE

    @property
    def is_ctrl(self) -> bool:
        """Return True if `ctrl` was also pressed."""
        return self.modifier == MOD_CTRL

    @property
    def is_shift(self) -> bool:
        """Return True if `shift` was also pressed."""
        return self.modifier == MOD_SHIFT
