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

    # pylint: disable=too-many-instance-attributes

    def __post_init__(self, grid: libcurses.Grid, max_users: int):
        """Build windows."""

        _nlines = int(max_users / 2) + 2 + 1  # 2=borders (top and bottom), 1=header.
        # 124=len(self._scoreboard._formatted_header) + 2=borders (left and right) + 1=padding
        # _ncols = min(124, int(2 * grid.ncols / 3))
        _ncols = int(grid.ncols / 2)

        # top-left
        self.chatwin_blu = grid.box(
            "chatwin_blu",
            nlines=_nlines,
            ncols=_ncols,
            left=grid,
            top=grid,
        )

        # stack blu
        self.scorewin_blu = grid.box(
            "scorewin_blu",
            nlines=_nlines,
            ncols=_ncols,
            left=self.chatwin_blu,
            top2b=self.chatwin_blu,
        )

        # top-right
        self.chatwin_red = grid.box(
            "chatwin_red",
            nlines=_nlines,
            ncols=0,
            left2r=self.chatwin_blu,
            right=grid,
            top=grid,
        )

        # stack red
        self.scorewin_red = grid.box(
            "scorewin_red",
            nlines=_nlines,
            ncols=0,
            left2r=self.scorewin_blu,
            right=grid,
            top2b=self.chatwin_red,
        )

        # bottom-left
        self.status_win = grid.box(
            "status",
            nlines=3,
            ncols=grid.ncols * 2 // 3,
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

        # section 3 - fills gap between sections 2 and 4
        self.user_win = grid.box(
            "user",
            nlines=0,
            ncols=min(62, grid.ncols // 2),  # 62: see get_weapon_state
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
