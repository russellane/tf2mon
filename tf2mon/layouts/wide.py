"""Wide layout."""

import libcurses

from tf2mon.baselayout import BaseLayout


class WideLayout(BaseLayout):
    """Wide layout.

    +-------------------+----------------------+
    | chatwin_blu       | chatwin_red          |  section 1
    |                   |                      |
    +-------------------+----------------------+
    | scorewin_blu      | scorewin_red         |  section 2
    |                   |                      |
    +--------------+----+----------------------+
    | user_win     | logger_win                |  section 3
    |              |                           |
    +--------------+--------+------------------+
    | status_win            | cmdline_win      |  section 4
    +-----------------------+------------------+
    """

    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-instance-attributes

    def __post_init__(self, grid: libcurses.Grid, max_users: int):
        """Build windows."""

        #
        #

        # section 1
        self.chatwin_blu = grid.box(
            "chatwin_blu",
            nlines=10,
            ncols=int(grid.ncols / 2),
            left=grid,
            top=grid,
        )

        self.chatwin_red = grid.box(
            "chatwin_red",
            nlines=0,
            ncols=0,
            left2r=self.chatwin_blu,
            right=grid,
            top=self.chatwin_blu,
            bottom=self.chatwin_blu,
        )

        # section 2
        self.scorewin_blu = grid.box(
            "scorewin_blu",
            nlines=int(max_users / 2) + 2 + 1,  # 2=borders (top and bottom), 1=header.
            ncols=int(grid.ncols / 2),
            left=grid,
            top2b=self.chatwin_blu,
        )

        self.scorewin_red = grid.box(
            "scorewin_red",
            nlines=0,
            ncols=0,
            left2r=self.scorewin_blu,
            right=grid,
            top=self.scorewin_blu,
            bottom=self.scorewin_blu,
        )

        # section 4
        self.status_win = grid.box(
            "status",
            nlines=3,
            ncols=int(2 * grid.ncols / 3),
            left=grid,
            bottom=grid,
        )

        self.cmdline_win = grid.box(
            "cmdline",
            nlines=3,
            ncols=0,
            left2r=self.status_win,
            right=grid,
            bottom=grid,
        )

        # section 3 - fills gap between sections 2 and 4
        self.user_win = grid.box(
            "user",
            nlines=0,
            ncols=int(grid.ncols / 3),
            left=grid,
            top2b=self.scorewin_blu,
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
