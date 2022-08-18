"""Collection of `User` objects."""

from loguru import logger

import tf2mon
from tf2mon.steamid import BOT_STEAMID, parse_steamid
from tf2mon.user import Team, User, UserState


class UserManager:
    """Collection of `User` objects."""

    def __init__(self):
        """Initialize `User` manager."""

        self._users_by_username = {}
        self._users_by_userid = {}
        self._users_by_steamid = {}
        self._teams_by_steamid = {}
        self.kicked_userids = {}

    def find_username(self, username):
        """Return `User` with the matching `username` from pool.

        Create and add to pool, if not already there.
        User is always "found"; an object is always returned.
        """

        username = username.replace(";", ".")

        if not (user := self._users_by_username.get(username)):
            user = User(username)
            self._users_by_username[user.username] = user
            logger.log("ADDUSER", user)

        # reset inactivity counter
        if user.state == UserState.INACTIVE:
            logger.debug(f"Active again {user}")
            user.state = UserState.ACTIVE
        user.n_status_checks = 0
        return user

    def status(self, s_userid, username, s_steamid, s_elapsed: str, ping) -> None:
        """Respond to `gameplay.status` event."""

        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-locals

        tf2mon.monitor.ui.notify_operator = False

        if not (steamid := parse_steamid(s_steamid)):
            return  # invalid

        userid = int(s_userid)
        user = None

        if steamid != BOT_STEAMID and (user := self._users_by_steamid.get(steamid)):
            if user.username and user.username != username:
                logger.warning(f"{steamid.id} change username `{user.username}` to `{username}`")
                user.username = username
                if user.player:
                    user.player.track_appearance(username)

            if user.userid and user.userid != userid:
                logger.warning(f"{steamid.id} change userid `{user.userid}` to `{userid}`")
                user.userid = userid

        if not user:
            user = self.find_username(username)

        if not user.userid:
            user.userid = userid
            self._users_by_userid[userid] = user

        if not user.steamid:
            user.steamid = steamid
            self._users_by_steamid[steamid] = user

        #
        mdy = s_elapsed.split(":")
        if len(mdy) == 2:
            _h, _m, _s = 0, int(mdy[0]), int(mdy[1])
            user.elapsed = (_m * 60) + _s
        elif len(mdy) == 3:
            _h, _m, _s = int(mdy[0]), int(mdy[1]), int(mdy[2])
            user.elapsed = (_h * 3600) + (_m * 60) + _s
        else:
            _h, _m, _s = 0, 0, 0
            user.elapsed = 0

        # hh:mm:ss
        #     0:00
        _ss = f"{_s:02}"
        if not _h:
            _mm = f"{_m:5}"
            user.s_elapsed = _mm + ":" + _ss
        else:
            _hh = f"{_h:2}"
            _mm = f"{_m:02}"
            user.s_elapsed = _hh + ":" + _mm + ":" + _ss

        #
        user.ping = ping
        logger.log("STATUS", user)

        #
        if not user.team and (team := self._teams_by_steamid.get(steamid)):
            user.assign_team(team)

        #
        if not user.steamplayer:
            user.vet()

    def lobby(self, s_steamid, teamname):
        """Respond to `gameplay.lobby` event."""

        # this will not be called for games on local server with bots
        # or community servers; only on valve matchmaking servers.

        if not (steamid := parse_steamid(s_steamid)):
            return  # invalid

        if teamname == "TF_GC_TEAM_INVADERS":
            team = Team.BLU
        elif teamname == "TF_GC_TEAM_DEFENDERS":
            team = Team.RED
        else:
            logger.critical(f"bad teamname {teamname!r} steamid {steamid}")
            return

        if old_team := self._teams_by_steamid.get(steamid):
            # if we've seen this steamid before...
            if old_team != team:
                # ...and
                logger.warning(f"{steamid.id} change team `{old_team}` to `{team}`")
        else:
            logger.log("ADDLOBBY", f"{team} {steamid.id}")

        #
        self._teams_by_steamid[steamid] = team

    def active_users(self):
        """Return list of active users."""

        yield from [x for x in self._users_by_username.values() if x.state == UserState.ACTIVE]

    def active_team_users(self, team):
        """Return list of active users on `team`."""

        yield from sorted(
            [
                x
                for x in self._users_by_username.values()
                if x.state == UserState.ACTIVE and x.team == team
            ],
            key=tf2mon.monitor.controls["SortOrderControl"].value,
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
