import re

import tf2mon
import tf2mon.monitor as Monitor
from tf2mon.game import GameEvent
from tf2mon.steamid import parse_steamid
from tf2mon.user import Team


class GameLobbyEvent(GameEvent):

    # tf_lobby_debug
    # "Member[22] [U:1:99999999]  team = TF_GC_TEAM_INVADERS  type = MATCH_PLAYER"

    pattern = r"\s*(?:Member|Pending)\[\d+\] (?P<steamid>\S+)\s+team = (?P<teamname>\w+)"

    def handler(self, match: re.Match) -> None:

        # this will not be called for games on local server with bots
        # or community servers; only on valve matchmaking servers.

        _leader, s_steamid, teamname = match.groups()

        if not (steamid := parse_steamid(s_steamid)):
            return  # invalid

        if teamname == "TF_GC_TEAM_INVADERS":
            team = Team.BLU
        elif teamname == "TF_GC_TEAM_DEFENDERS":
            team = Team.RED
        else:
            tf2mon.logger.critical(f"bad teamname {teamname!r} steamid {steamid}")
            return

        if old_team := Monitor.users.teams_by_steamid.get(steamid):
            # if we've seen this steamid before...
            if old_team != team:
                # ...and
                tf2mon.logger.warning(f"{steamid.id} change team `{old_team}` to `{team}`")
        else:
            tf2mon.logger.log("ADDLOBBY", f"{team} {steamid.id}")

        #
        Monitor.users.teams_by_steamid[steamid] = team
