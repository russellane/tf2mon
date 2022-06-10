"""Base class for display layout."""

import curses
from dataclasses import KW_ONLY, InitVar, dataclass

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
    chatwin_blu: curses.window = None
    chatwin_red: curses.window = None
    scorewin_blu: curses.window = None
    scorewin_red: curses.window = None
    user_win: curses.window = None
    kicks_win: curses.window = None
    spams_win: curses.window = None
    duels_win: curses.window = None
    logger_win: curses.window = None
    status_win: curses.window = None
    cmdline_win: curses.window = None

    def __post_init__(self, grid: libcurses.Grid, max_users: int):
        """Build windows."""
        _ = grid  # unused
        _ = max_users  # unused
