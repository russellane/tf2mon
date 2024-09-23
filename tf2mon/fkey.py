"""Function Keys."""

from __future__ import annotations

import curses
import curses.ascii
import re
from dataclasses import dataclass, field
from typing import Any, ClassVar, Pattern

# Values for `modifier`; also used as `shortname` prefix.
MOD_BASE = ""
MOD_CTRL = "c"
MOD_SHIFT = "s"


class FKey:
    """The simultaneous pressing of a base key and an optional modifier key."""

    pattern: ClassVar[Pattern[str]] = re.compile(r"^(?:(SHIFT|CTRL)\+)?(F)?(.+)$")

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

    # physical keys, by `name`.
    pkeys: ClassVar[dict[str, PKey]] = {}

    # Keyname in TF2 terms, with optional modifier "shift+" or "ctrl+" (not both).
    # e.g., "A", "shift+A", "ctrl+KP_LEFTARROW".
    keyspec: str

    name: str  # TF2 terms: "B", "KP_LEFTARROW", "F1"
    modifier: str  # MOD_BASE, MOD_CTRL or MOD_SHIFT
    key: int  # ord("B"), curses.KEY_LEFT, curses.KEY_F1
    shortname: str  # for status-line.
    longname: str  # for `--help`.
    pkey: PKey  # physical key

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
        self.name = (eff or "") + key  # TF2 terms: "B", "KP_LEFTARROW", "F1"

        self.modifier = MOD_BASE
        if mod:
            if mod == "SHIFT":
                self.modifier = MOD_SHIFT
            elif mod == "CTRL":
                self.modifier = MOD_CTRL
            else:
                raise ValueError("keyspec", self.keyspec)

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

        self.shortname = self.modifier + self.name  # display name

        self.longname = ""
        if self.modifier == MOD_SHIFT:
            self.longname = "shift+"
        elif self.modifier == MOD_CTRL:
            self.longname = "ctrl+"
        self.longname += self.name

        pkey = self.__class__.pkeys.get(self.name)
        if not pkey:
            pkey = PKey(self.name)
            self.__class__.pkeys[self.name] = pkey
        self.pkey = pkey

    def __repr__(self) -> str:
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

    @property
    def is_ascii(self) -> bool:
        """Return True if this is an ascii key."""
        return curses.ascii.isascii(self.key)

    def bind(self, payload: Any) -> None:
        """Bind `payload` to this key."""

        if self.is_ctrl:
            if self.pkey.ctrl:
                raise ValueError("duplicate keyspec", self.keyspec)
            self.pkey.ctrl = payload
        #
        elif self.is_shift:
            if self.pkey.shift:
                raise ValueError("duplicate keyspec", self.keyspec)
            self.pkey.shift = payload
        #
        else:
            if self.pkey.base:
                raise ValueError("duplicate keyspec", self.keyspec)
            self.pkey.base = payload


@dataclass
class PKey:
    """A physical key may perform `base`, `ctrl` and `shift` `Function`s."""

    name: str  # e.g., "A", "F1"
    base: Any | None = field(default=None, init=False)
    ctrl: Any | None = field(default=None, init=False)
    shift: Any | None = field(default=None, init=False)

    @property
    def bindings(self) -> list[Any]:
        """Return list of `payload`s bound to this `PKey`."""
        return [x for x in [self.base, self.ctrl, self.shift] if x is not None]
