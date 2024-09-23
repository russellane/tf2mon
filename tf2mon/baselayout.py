"""Base class for display layout."""

import curses
from dataclasses import KW_ONLY, InitVar, dataclass, field

import libcurses


@dataclass(slots=True)
class BaseLayout:
    """Base class for display layout.

    Each layout must initialize:
        - logger_win
        - status_win
        - cmdline_win
    others may remain undefined.
    """

    # pylint: disable=too-many-instance-attributes

    grid: InitVar[libcurses.Grid]
    max_users: InitVar[int] = 32
    _: KW_ONLY
    chatwin_blu: curses.window | None = None
    chatwin_red: curses.window | None = None
    scorewin_blu: curses.window = field(init=False)
    scorewin_red: curses.window = field(init=False)
    user_win: curses.window | None = None
    kicks_win: curses.window | None = None
    spams_win: curses.window | None = None
    duels_win: curses.window | None = None
    logger_win: curses.window = field(init=False)
    status_win: curses.window = field(init=False)
    cmdline_win: curses.window = field(init=False)

    def __post_init__(self, grid: libcurses.Grid, max_users: int) -> None:
        """Build windows."""
        _ = grid  # unused
        _ = max_users  # unused
