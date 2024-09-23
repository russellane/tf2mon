from typing import Match

from loguru import logger

import tf2mon
from tf2mon.gameevent import GameEvent
from tf2mon.steamid import parse_steamid
from tf2mon.user import Team


class GameLobbyEvent(GameEvent):

    # tf_lobby_debug
    # "Member[22] [U:1:99999999]  team = TF_GC_TEAM_INVADERS  type = MATCH_PLAYER"

    pattern = r"\s*(?:Member|Pending)\[\d+\] (?P<steamid>\S+)\s+team = (?P<teamname>\w+)"

    def handler(self, match: Match[str]) -> None:

        # this will not be called for games on local server with bots
        # or community servers; only on valve matchmaking servers.

        s_steamid, teamname = match.groups()

        if not (steamid := parse_steamid(s_steamid)):
            return  # invalid

        if teamname == "TF_GC_TEAM_INVADERS":
            team = Team.BLU
        elif teamname == "TF_GC_TEAM_DEFENDERS":
            team = Team.RED
        else:
            logger.critical(f"bad teamname {teamname!r} steamid {steamid}")
            return

        if old_team := tf2mon.users.teams_by_steamid.get(steamid):
            # if we've seen this steamid before...
            if old_team != team:
                # ...and
                logger.warning(f"{steamid.id} change team `{old_team}` to `{team}`")
        else:
            logger.log("ADDLOBBY", f"{team} {steamid.id}")

        #
        tf2mon.users.teams_by_steamid[steamid] = team
