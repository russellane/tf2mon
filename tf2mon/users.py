"""Collection of `User` objects."""

import re
from typing import Iterator

from fuzzywuzzy import fuzz  # type: ignore
from loguru import logger

import tf2mon
from tf2mon.player import Player
from tf2mon.racist import is_racist_text
from tf2mon.user import Team, User, UserKey


class Users:
    """Collection of `User`s."""

    def __init__(self) -> None:
        """Initialize collection of `User`s."""

        self.users_by_username: dict[UserKey, User] = {}
        self.users_by_steamid: dict[int, User] = {}
        self.teams_by_steamid: dict[int, Team] = {}
        self.me: User
        self.my: User
        self._max_status_checks = 2

    def __getitem__(self, username: UserKey) -> User:
        """Create user `username` if non-existent, and return user `username`."""

        username = UserKey(username.replace(";", "."))

        if not (user := self.users_by_username.get(username)):
            user = User(username)
            self.users_by_username[UserKey(user.username)] = user
            logger.log("ADDUSER", user)

            if self._is_cheater_name(user):
                user.kick(Player.CHEATER)

            if is_racist_text(username):
                user.kick(Player.RACIST)

        # reset inactivity counter
        if not user.is_active:
            logger.debug(f"Active again {user}")
        user.n_status_checks = 0
        return user

    def active_users(self) -> Iterator[User]:
        """Yield active users (unsorted)."""

        yield from [x for x in self.users_by_username.values() if x.is_active]

    def sorted(self) -> Iterator[User]:
        """Yield active users in sort order."""

        yield from sorted(
            self.active_users(),
            key=tf2mon.SortOrderControl.value,
        )

    def kick_userid(self, userid: int, attr: str) -> None:
        """Kick `userid` reason `attr`."""

        users = [x for x in self.users_by_username.values() if x.userid == userid]
        if len(users) == 1:
            users[0].kick(attr)
        else:
            logger.error(f"bad userid {userid!r}")

    def kick_my_last_killer(self, attr: str) -> None:
        """Kick the last user who killed the operator."""

        if self.my.last_killer:
            self.my.last_killer.kick(attr)
        else:
            logger.warning("no last killer")

    def check_status(self) -> None:
        """Delete users that appear to have left the game.

        We are called in response to TF2MON-PUSH; which may have came long
        before `status` finished sending everything; and we don't have a
        way to detect when `status` finishes; so we'll never be completely
        current. That's why `_max_status_checks` should be at least 2 or 3.
        """

        for user in [x for x in self.users_by_username.values() if x != self.me]:
            was_active = user.is_active
            user.n_status_checks += 1
            if was_active and not user.is_active:
                logger.log("INACTIVE", user)

    def switch_teams(self) -> None:
        """Switch teams."""

        for user in self.active_users():
            user.team = user.opposing_team

    re_cheater_names = re.compile(
        "|".join(
            [
                r"^(\(\d+\))?Sydney",
                r"Swonk Bot",
                r"spoooky braaaap",
                r"Bot Removal Service",
                r"^\[g0tb0t\]Church-of-myg0t",
            ]
        )
    )

    def _is_cheater_name(self, user: User) -> bool:

        if self.re_cheater_names.search(user.username):
            return True

        for _user in [x for x in self.active_users() if x.steamplayer and not x.player]:
            ratio = fuzz.ratio(user.username, _user.username)
            if ratio > 80:
                logger.log("FUZZ", f"ratio {ratio} `{user.username}` vs `{_user.username}`")
                # Careful, this might be a legitimate name-change, not a cheating name-stealer.
                _user.cloner = user  # point the original user to the clone
                user.clonee = _user  # point the clone to the original user
                return True

        return False
