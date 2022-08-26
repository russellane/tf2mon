"""Collection of `User` objects."""

from typing import Iterator

from loguru import logger

import tf2mon
from tf2mon.user import User, UserState


class Users:
    """Collection of `User`s."""

    _max_status_checks = 2

    def __init__(self):
        """Initialize collection of `User`s."""

        self.users_by_username: dict[str, User] = {}
        self.users_by_steamid: dict[int, User] = {}
        self.teams_by_steamid: dict[int, User] = {}

    def __getitem__(self, username: str) -> User:
        """Create user `username` if non-existent, and return user `username`."""

        username = username.replace(";", ".")

        if not (user := self.users_by_username.get(username)):
            user = User(username)
            self.users_by_username[user.username] = user
            logger.log("ADDUSER", user)

        # reset inactivity counter
        if user.state == UserState.INACTIVE:
            logger.debug(f"Active again {user}")
            user.state = UserState.ACTIVE
        user.n_status_checks = 0
        return user

    def active_users(self) -> Iterator[User]:
        """Yield active users (unsorted)."""

        yield from [x for x in self.users_by_username.values() if x.state == UserState.ACTIVE]

    def sorted(self) -> Iterator[User]:
        """Yield active users in sort order."""

        yield from sorted(
            self.active_users(),
            key=tf2mon.controls["SortOrderControl"].value,
        )

    def kick_userid(self, userid, attr):
        """Kick `userid` reason `attr`."""

        users = [x for x in self.users_by_username.values() if x.userid == userid]
        if len(users) == 1:
            users[0].kick(attr)
        else:
            logger.error(f"bad userid {userid!r}")

    def check_status(self):
        """Delete users that appear to have left the game.

        We are called in response to TF2MON-PUSH; which may have came long
        before `status` finished sending everything; and we don't have a
        way to detect when `status` finishes; so we'll never be completely
        current. That's why `_max_status_checks` should be at least 2 or 3.
        """

        for user in list(self.users_by_username.values()):
            if user == tf2mon.monitor.me:
                continue
            user.n_status_checks += 1
            if user.n_status_checks == self._max_status_checks:
                logger.log("INACTIVE", user)
                user.state = UserState.INACTIVE

    def switch_teams(self):
        """Switch teams."""

        for user in self.active_users():
            user.assign_team(user.opposing_team)
