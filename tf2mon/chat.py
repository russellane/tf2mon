"""Player `Chat` message."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tf2mon.user import User, UserStats


@dataclass
class Chat:
    """Player `Chat` message."""

    user: User
    teamflag: bool
    msg: str
    timestamp: float | None = field(default=None)
    #
    s_timestamp: str | None = field(default=None, init=False)
    stats: UserStats | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Initialize data and other attributes."""

        if not self.timestamp:
            self.timestamp = time.time()

        self.s_timestamp = time.strftime("%T", time.localtime(self.timestamp))
        # _dt = datetime.datetime.fromtimestamp(self.timestamp)
        # self.s_timestamp = _dt.strftime("%T.%f")  # [:-4]

        self.stats = self.user.snap_stats()
