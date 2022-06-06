"""Collection of `User` objects."""

from loguru import logger

from tf2mon.steamplayer import SteamPlayer
from tf2mon.ui import SORT_ORDER
from tf2mon.user import User, UserState


class UserManager:
    """Collection of `User` objects."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, monitor):
        """Initialize `User` manager."""

        self.monitor = monitor

        # The pool.

        self._users_by_username = {}
        self._users_by_userid = {}
        self._users_by_steamid = {}
        self._teams_by_steamid = {}
        self.kicked_userids = {}

        # Some methods return a sorted list of users.
        # Names must match scoreboard column headings.

        self._sort_keys = {
            SORT_ORDER.K: lambda x: (-x.nkills, x.username_upper),
            SORT_ORDER.KD: lambda x: (-x.kdratio, -x.nkills, x.username_upper),
            SORT_ORDER.STEAMID: lambda x: (x.steamid.id if x.steamid else 0, x.username_upper),
            SORT_ORDER.USERNAME: lambda x: x.username_upper,
        }
        self._sort_key = self._sort_keys[SORT_ORDER.KD]

    def set_sort_order(self, sort_order):
        """Set sort-key used by `active_team_users`."""

        self._sort_key = self._sort_keys.get(sort_order)

    def delete(self, user):
        """Remove `user` from pool."""

        try:
            if user.last_killer and user.last_killer.last_victim == user:
                user.last_killer.last_victim = None

            if user.last_victim and user.last_victim.last_killer == user:
                user.last_victim.last_killer = None

            if user.cloner:
                user.cloner.clonee = None

            if user.clonee:
                user.clonee.cloner = None

            del self._users_by_username[user.username]
            del self._users_by_userid[user.userid]

            if user.steamid:
                del self._users_by_steamid[user.steamid]
                del self._teams_by_steamid[user.steamid]

        except KeyError:
            pass

    def find_username(self, username):
        """Return `User` with the matching `username` from pool.

        Create and add to pool, if not already there.
        User is always "found"; an object is always returned.
        """

        username = username.replace(";", ".")

        if not (user := self._users_by_username.get(username)):
            user = User(self.monitor, username)
            self._users_by_username[user.username] = user
            logger.log("ADDUSER", user)

        # reset inactivity counter
        user.n_status_checks = 0
        return user

    def status(self, userid, username, steamid, ping) -> None:
        """Respond to `gameplay.status` event."""

        user = None

        if steamid.id != SteamPlayer.BOT_STEAMID and (
            user := self._users_by_steamid.get(steamid)
        ):
            if user.username and user.username != username:
                logger.warning(f"{steamid} changed username from {user.username} to {username}")
            if user.userid and user.userid != userid:
                logger.warning(f"{steamid} changed userid from {user.userid} to {userid}")

        if not user:
            user = self.find_username(username)
            if user.userid and user.userid != userid:
                logger.warning(f"{username} changed userid from {user.userid} to {userid}")
            if user.steamid and user.steamid != steamid:
                logger.error(f"{username} changed steamid from {user.steamid} to {steamid}")

        if not user.userid:
            user.userid = userid
            self._users_by_userid[userid] = user

        if not user.steamid:
            user.steamid = steamid
            self._users_by_steamid[steamid] = user

        #
        user.ping = ping
        logger.log("STATUS", user)

        #
        if not user.team and (team := self._teams_by_steamid.get(steamid)):
            user.assign_team(team)

    def lobby(self, steamid, team):
        """Respond to `gameplay.lobby` event."""

        if old_team := self._teams_by_steamid.get(steamid):
            # if we've seen this steamid before...
            if old_team != team:
                # ...and
                logger.warning(f"{steamid} changed team from {old_team} to {team}")
        else:
            logger.log("ADDLOBBY", f"{team} {steamid}")

        #
        self._teams_by_steamid[steamid] = team

    def active_users(self):
        """Return list of active users."""

        yield from [x for x in self._users_by_username.values() if x.state == UserState.ACTIVE]

    def active_team_users(self, team):
        """Return list of active users on `team`."""

        assert self._sort_key

        yield from sorted(
            [
                x
                for x in self._users_by_username.values()
                if x.state == UserState.ACTIVE and x.team == team
            ],
            key=self._sort_key,
        )

    def kick_userid(self, userid, attr):
        """Kick `userid` reason `attr`."""

        if user := self._users_by_userid.get(userid):
            user.kick(attr)
        else:
            logger.error(f"bad userid {userid!r}")

    _max_status_checks = 2

    def check_status(self):
        """Delete users that appear to have left the game.

        We are called in response to TF2MON-PUSH; which may have came long
        before `status` finished sending everything; and we don't have a
        way to detect when `status` finishes; so we'll never be completely
        current. That's why `_max_status_checks` should be at least 2 or 3.
        """

        for user in list(self._users_by_username.values()):
            if user == self.monitor.me:
                continue
            user.n_status_checks += 1
            if user.n_status_checks >= self._max_status_checks:
                logger.log(
                    "Inactive",
                    f"{user.n_status_checks} >= {self._max_status_checks} {user.username!r}",
                )
                self.delete(user)

    def switch_teams(self):
        """Switch teams."""

        for user in self.active_users():
            user.assign_team(user.opposing_team)
