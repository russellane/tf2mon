from typing import Match

from loguru import logger

import tf2mon
from tf2mon.gameevent import GameEvent
from tf2mon.steamid import BOT_STEAMID, parse_steamid
from tf2mon.user import UserKey


class GameStatusEvent(GameEvent):

    # status
    # "# userid name                uniqueid            connected ping loss state"
    # "#     29 "Bob"               [U:1:99999999]      01:24       67    0 active"
    # "#    158 "Jones"             [U:1:9999999999]     2:21:27    78    0 active
    # "#      3 "Nobody"            BOT                                     active

    pattern = r'#\s*(?P<s_userid>\d+) "(?P<username>.+)"\s+(?P<steamid>\S+)(?:\s+(?P<elapsed>[\d:]+)\s+(?P<ping>\d+))'

    def handler(self, match: Match[str]) -> None:

        # pylint: disable=too-many-branches
        # pylint: disable=too-many-locals

        s_userid, username, s_steamid, s_elapsed, ping = match.groups()

        tf2mon.ui.notify_operator = False

        if not (steamid := parse_steamid(s_steamid)):
            return  # invalid

        userid = int(s_userid)
        user = None

        if steamid != BOT_STEAMID and (user := tf2mon.users.users_by_steamid.get(steamid)):
            if user.username and user.username != username:
                logger.warning(f"{steamid.id} change username `{user.username}` to `{username}`")
                user.username = username
                if user.player:
                    user.player.track_appearance(username)

            if user.userid and user.userid != userid:
                logger.warning(f"{steamid.id} change userid `{user.userid}` to `{userid}`")
                user.userid = userid

        if not user:
            user = tf2mon.users[UserKey(username)]

        user.dirty = True

        if not user.userid:
            user.userid = userid

        if not user.steamid:
            user.steamid = steamid
            tf2mon.users.users_by_steamid[steamid] = user

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
        user.ping = int(ping)
        logger.log("STATUS", user)

        #
        if not user.team and (team := tf2mon.users.teams_by_steamid.get(steamid)):
            user.team = team

        #
        if not user.steamplayer:
            user.vet()
