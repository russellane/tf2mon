"""Full layout."""

import libcurses

from tf2mon.baselayout import BaseLayout


class FullLayout(BaseLayout):
    """Full layout.

    +-------------------+------------+---------+
    | score blu         | chat blu   | kicks   |
    |                   |            |         |
    +-------------------+------------+---------+
    | score red         | chat red   | spams   |
    |                   |            |         |
    +--------------+----+------------+---------+
    | user         | logger                    |
    |              |                           |
    +--------------+--------+------------------+
    | status                | cmdline          |
    +-----------------------+------------------+
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
        self.scorewin_red = grid.box(
            "scorewin_red",
            nlines=_nlines,
            ncols=_ncols,
            left=grid,
            top2b=self.scorewin_blu,
        )

        # bottom-left
        self.status_win = grid.box(
            "status",
            nlines=3,
            ncols=_ncols,
            left=grid,
            bottom=grid,
        )

        # bottom-right
        self.cmdline_win = grid.box(
            "cmdline",
            nlines=3,
            ncols=0,
            left2r=self.status_win,
            right=grid,
            bottom=grid,
        )

        #
        self.chatwin_blu = grid.box(
            "chatwin_blu",
            nlines=0,
            ncols=60,
            left2r=self.scorewin_blu,
            top=self.scorewin_blu,
            bottom=self.scorewin_blu,
        )

        self.chatwin_red = grid.box(
            "chatwin_red",
            nlines=0,
            ncols=60,
            left2r=self.scorewin_red,
            top=self.scorewin_red,
            bottom=self.scorewin_red,
        )

        #
        self.kicks_win = grid.box(
            "kicks_win",
            nlines=0,
            ncols=0,
            left2r=self.chatwin_blu,
            right=grid,
            top=self.chatwin_blu,
            bottom=self.chatwin_blu,
        )

        self.spams_win = grid.box(
            "spams_win",
            nlines=0,
            ncols=0,
            left2r=self.chatwin_red,
            right=grid,
            top=self.chatwin_red,
            bottom=self.chatwin_red,
        )

        # section 3 - fills gap between sections 2 and 4
        self.user_win = grid.box(
            "user",
            nlines=0,
            ncols=min(62, grid.ncols // 2),  # 62: see get_weapon_state
            left=grid,
            top2b=self.scorewin_red,
            bottom2t=self.status_win,
        )

        self.logger_win = grid.box(
            "logwin",
            nlines=0,
            ncols=0,
            left2r=self.user_win,
            right=grid,
            top=self.user_win,
            bottom=self.user_win,
        )
