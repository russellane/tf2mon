"""Default layout."""

import libcurses

from tf2mon.baselayout import BaseLayout


class DefaultLayout(BaseLayout):
    """Default layout.

    +-------------------+-----------+----------+
    | score blu         | kicks     | spams    |
    |                   |           |          |
    +-------------------+           |          |
    | score red         |           |          |
    |                   |           |          |
    +-------------------+-----------+----------+
    | chats (merged)    | duels                |
    |                   |                      |
    +-------------------+                      |
    | logger            |                      |
    |                   |                      |
    +-------------------+----------------------+
    | status            | cmdline              |
    +-------------------+----------------------+
    """

    # pylint: disable=too-many-instance-attributes

    def __post_init__(self, grid: libcurses.Grid, max_users: int) -> None:
        """Build windows."""

        _nlines = int(max_users / 2) + 2 + 1  # 2=borders (top and bottom), 1=header.
        # 124=len(self._scoreboard._formatted_header) + 2=borders (left and right) + 1=padding
        # _ncols = min(124, int(2 * grid.ncols / 3))
        _ncols = int(grid.ncols / 2)

        # top-left
        self.scorewin_blu = grid.box(
            "scorewin_blu",
            nlines=_nlines,
            ncols=_ncols,
            left=grid,
            top=grid,
        )

        # stack scoreboards
        gap_top = self.scorewin_red = grid.box(
            "scorewin_red",
            nlines=_nlines,
            ncols=_ncols,
            left=grid,
            top2b=self.scorewin_blu,
        )

        # -- leave vertical gap --

        # bottom-left
        gap_bottom = self.status_win = grid.box(
            "status",
            nlines=3,
            ncols=_ncols,
            left=grid,
            bottom=grid,
        )

        # -- fill vertical gap with:
        # -- 50% chats
        # -- 50% logger

        _nlines = int(
            ((gap_bottom.getbegyx()[0] - gap_top.getbegyx()[0]) - gap_top.getmaxyx()[0]) / 2
        )

        self.chatwin_blu = grid.box(
            "chatwin_blu",
            nlines=_nlines,
            ncols=_ncols,
            left=grid,
            top2b=self.scorewin_red,
        )

        self.logger_win = grid.box(
            "logwin",
            nlines=0,
            ncols=_ncols,
            left=grid,
            top2b=self.chatwin_blu,
            bottom2t=self.status_win,
        )

        # -------------------------------------------------------------------------------

        # top-right
        gap_top_grid = grid.win

        # -- leave vertical gap --

        # bottom-right
        gap_bottom = self.cmdline_win = grid.box(
            "cmdline",
            nlines=3,
            ncols=0,
            left2r=self.status_win,
            right=grid,
            bottom=grid,
        )

        # -- fill vertical gap with:
        # -- 50% kicks/spams
        # -- 50% duels
        _nlines = int((gap_bottom.getbegyx()[0] - gap_top_grid.getbegyx()[0]) / 2)

        # kicks/spams
        gap_left = self.scorewin_red
        # -- fill horizontal gap with:
        # -- 50% kicks (left)
        # -- 50% spams (right)
        _ncols = int((grid.ncols - gap_left.getmaxyx()[1]) / 2)

        # top-right, left-half
        self.kicks_win = grid.box(
            "kicks_win",
            nlines=_nlines,
            ncols=_ncols,
            left2r=self.chatwin_blu,
            top=grid,
        )

        # top-right, right-half
        self.spams_win = grid.box(
            "spams_win",
            nlines=_nlines,
            ncols=0,
            left2r=self.kicks_win,
            right=grid,
            top=grid,
        )

        # final gap
        self.duels_win = grid.box(
            "duels_win",
            nlines=0,
            ncols=0,
            left2r=self.chatwin_blu,
            right=grid,
            top2b=self.kicks_win,
            bottom2t=self.cmdline_win,
        )
