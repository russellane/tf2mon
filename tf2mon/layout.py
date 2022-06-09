"""Grid Layout."""

import curses
from dataclasses import KW_ONLY, InitVar, dataclass

import libcurses


@dataclass(slots=True)
class Layout:
    """Grid Layout."""

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
