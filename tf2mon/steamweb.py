"""Interface to `ISteamUser.GetPlayerSummaries`."""

import time

import steam.webapi  # type: ignore
from loguru import logger

from tf2mon.steamid import BOT_STEAMID, SteamID
from tf2mon.steamplayer import SteamPlayer

MAX_AGE = 2 * 60 * 60


class SteamWebAPI:
    """Interface to `ISteamUser.GetPlayerSummaries`.

    Results are cached to avoid banging the server.
    """

    def __init__(self, webapi_key: str):
        """Initialize interface."""

        if webapi_key:
            self._webapi = steam.webapi.WebAPI(key=webapi_key)
        else:
            self._webapi = None
            logger.warning("Running without `webapi_key`")

        self._nbots = 0

    def fetch_steamid(self, steamid: int) -> SteamPlayer:
        """Lookup and return `SteamPlayer` with matching `steamid`.

        Use web service to get "Player Summary" of given `steamid`.
        Create dummy object for game bots.
        """

        now = int(time.time())

        if steamid == BOT_STEAMID.id:
            # create a dummy steamid for this bot; (not a hacker, a real game bot)
            self._nbots += 1
            return SteamPlayer(
                steamid=steamid,
                personaname="",
                profileurl="",
                personastate=0,
                realname="",
                timecreated=now - (self._nbots * 86400),
                loccountrycode="US",
                locstatecode="IL",
                loccityid="CHGO",
            )

        if not SteamID(steamid).is_valid():
            return SteamPlayer(steamid=steamid, personaname="???", timecreated=now, mtime=now)

        # it's not a game bot; look in database.
        steamplayer = SteamPlayer.fetch_steamid(steamid)

        if steamplayer and steamplayer.mtime > now - MAX_AGE:
            logger.debug("current")
            return steamplayer
        if steamplayer:
            logger.debug("expired")

        # not current or not in cache; call web service.
        player_summaries = self._get_player_summaries([SteamID(steamid)])

        if len(player_summaries) < 1:
            return SteamPlayer(steamid=steamid, personaname="???", timecreated=now, mtime=now)

        summary = player_summaries[0]

        steamplayer = SteamPlayer(
            steamid,
            summary.get("personaname", ""),
            summary.get("profileurl", ""),
            int(summary.get("personastate", 0)),
            summary.get("realname", ""),
            int(summary.get("timecreated", 0)),
            summary.get("loccountrycode", ""),
            summary.get("locstatecode", ""),
            summary.get("loccityid", ""),
            now,
        )

        steamplayer.upsert()
        return steamplayer

    def _get_player_summaries(self, steamids: list[SteamID]) -> list[dict[str, str]]:

        if not self._webapi:
            return []

        jdoc = self._webapi.call(
            "ISteamUser.GetPlayerSummaries", steamids=",".join([str(x.as_64) for x in steamids])
        )

        return list(jdoc["response"]["players"])
