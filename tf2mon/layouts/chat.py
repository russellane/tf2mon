"""Chat layout."""

import libcurses

from tf2mon.baselayout import BaseLayout


class ChatLayout(BaseLayout):
    """Chat layout.

    +-------------------+----------------------+
    | scorewin_blu      | scorewin_red         |  section 1
    |                   |                      |
    +-------------------+----------------------+
    | chatwin_blu       | chatwin_red          |  section 2
    |                   |                      |
    +--------------+----+----------------------+
    | user_win     | logger_win                |  section 3
    |              |                           |
    +--------------+--------+------------------+
    | status_win            | cmdline_win      |  section 4
    +-----------------------+------------------+
    """

    # pylint: disable=too-many-instance-attributes

    def __post_init__(self, grid: libcurses.Grid, max_users: int) -> None:
        """Build windows."""

        n_score_lines = int(max_users / 2) + 2 + 1  # 2=borders (top and bottom), 1=header.
        # 124=len(self._scoreboard._formatted_header) + 2=borders (left and right) + 1=padding
        # _ncols = min(124, int(2 * grid.ncols / 3))
        _ncols = int(grid.ncols / 2)

        n_avail = (grid.nlines - n_score_lines) - 1  # 1=border (between chat and user).

        min_n_chat_lines = 20
        max_n_user_lines = 20

        if n_avail < min_n_chat_lines + max_n_user_lines:
            n_chat_lines = int(n_avail / 2)
            n_user_lines = n_avail - n_chat_lines
        else:
            n_user_lines = max_n_user_lines
            n_chat_lines = n_avail - n_user_lines

        # A1 top-left
        self.scorewin_blu = grid.box(
            "scorewin_blu",
            top=grid,
            left=grid,
            nlines=n_score_lines,
            ncols=_ncols,
        )

        # B1 top-right
        self.scorewin_red = grid.box(
            "scorewin_red",
            top=grid,
            right=grid,
            nlines=n_score_lines,
            ncols=0,
            left2r=self.scorewin_blu,
        )

        # -------------------------------------
        # A2 leave vertical gap for chatwin_blu
        # -------------------------------------

        # A4 bottom-left
        self.status_win = grid.box(
            "status",
            bottom=grid,
            left=grid,
            nlines=3,
            ncols=grid.ncols * 2 // 3,
        )

        # B4 bottom-right
        self.cmdline_win = grid.box(
            "cmdline",
            bottom=grid,
            right=grid,
            nlines=3,
            ncols=0,
            left2r=self.status_win,
        )

        # A3 above bottom-left
        self.user_win = grid.box(
            "user",
            bottom2t=self.status_win,
            left=grid,
            nlines=n_user_lines,
            ncols=min(62, grid.ncols // 2),  # 62: see get_weapon_state
        )

        # B3 above bottom-right
        self.logger_win = grid.box(
            "logwin",
            bottom=self.user_win,
            right=grid,
            top=self.user_win,
            left2r=self.user_win,
            nlines=0,
            ncols=0,
        )

        # A2 below top-left
        self.chatwin_blu = grid.box(
            "chatwin_blu",
            top2b=self.scorewin_blu,
            left=grid,
            nlines=0,
            ncols=_ncols,
            bottom2t=self.user_win,
        )

        # B2 below top-right
        self.chatwin_red = grid.box(
            "chatwin_red",
            top2b=self.scorewin_red,
            right=grid,
            left2r=self.chatwin_blu,
            bottom2t=self.user_win,
            nlines=0,
            ncols=0,
        )
