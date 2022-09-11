import re

import tf2mon
import tf2mon.monitor as Monitor
from tf2mon.game import GameEvent
from tf2mon.steamid import BOT_STEAMID, parse_steamid


class GameStatusEvent(GameEvent):

    # status
    # "# userid name                uniqueid            connected ping loss state"
    # "#     29 "Bob"               [U:1:99999999]      01:24       67    0 active"
    # "#    158 "Jones"             [U:1:9999999999]     2:21:27    78    0 active
    # "#      3 "Nobody"            BOT                                     active

    pattern = r'#\s*(?P<s_userid>\d+) "(?P<username>.+)"\s+(?P<steamid>\S+)(?: \s+(?P<elapsed>[\d:]+)\s+(?P<ping>\d+))'

    def handler(self, match: re.Match) -> None:

        # pylint: disable=too-many-branches
        # pylint: disable=too-many-locals

        _leader, s_userid, username, s_steamid, s_elapsed, ping = match.groups()

        Monitor.ui.notify_operator = False

        if not (steamid := parse_steamid(s_steamid)):
            return  # invalid

        userid = int(s_userid)
        user = None

        if steamid != BOT_STEAMID and (user := Monitor.users.users_by_steamid.get(steamid)):
            if user.username and user.username != username:
                tf2mon.logger.warning(
                    f"{steamid.id} change username `{user.username}` to `{username}`"
                )
                user.username = username
                if user.player:
                    user.player.track_appearance(username)

            if user.userid and user.userid != userid:
                tf2mon.logger.warning(
                    f"{steamid.id} change userid `{user.userid}` to `{userid}`"
                )
                user.userid = userid

        if not user:
            user = Monitor.users[username]

        user.dirty = True

        if not user.userid:
            user.userid = userid

        if not user.steamid:
            user.steamid = steamid
            Monitor.users.users_by_steamid[steamid] = user

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
        tf2mon.logger.log("STATUS", user)

        #
        if not user.team and (team := Monitor.users.teams_by_steamid.get(steamid)):
            user.assign_team(team)

        #
        if not user.steamplayer:
            user.vet()
