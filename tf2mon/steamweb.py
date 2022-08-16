"""Interface to `ISteamUser.GetPlayerSummaries`."""

import time

import steam.webapi
from loguru import logger

from tf2mon.database import Database
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

    def find_steamid(self, steamid: SteamID) -> SteamPlayer:
        """Lookup and return `SteamPlayer` with matching `steamid`.

        Use web service to get "Player Summary" of given `steamid`.
        Create dummy object for game bots.
        """

        now = int(time.time())

        if steamid.id == BOT_STEAMID:
            # create a dummy steamid for this bot; (not a hacker, a real game bot)
            self._nbots += 1
            return SteamPlayer(
                {
                    "steamid": steamid.id,
                    "personaname": None,
                    "profileurl": "",
                    "personastate": 0,
                    "realname": "",
                    "timecreated": now - (self._nbots * 86400),
                    "loccountrycode": "US",
                    "locstatecode": "IL",
                    "loccityid": "CHGO",
                }
            )

        # it's not a game bot; look in database.
        steamplayer = SteamPlayer.find_steamid(steamid)

        if steamplayer and steamplayer.mtime > now - MAX_AGE:
            # logger.debug('current')
            return steamplayer
        # if steamplayer:
        #     logger.debug('expired')

        # not current or not in cache; call web service.
        player_summaries = self._get_player_summaries([steamid])

        if len(player_summaries) < 1:
            # unexpected!
            return SteamPlayer(
                {
                    "steamid": steamid.id,
                    "personaname": "???",
                    "profileurl": "",
                    "personastate": "?",
                    "realname": "",
                    "timecreated": now,
                    "loccountrycode": "",
                    "locstatecode": "",
                    "loccityid": "",
                }
            )

        steamplayer = SteamPlayer(player_summaries[0])

        try:
            Database().execute(
                "replace into steamplayers values(?,?,?,?,?,?,?,?,?,?)",
                (
                    steamplayer.steamid,
                    steamplayer.personaname,
                    steamplayer.profileurl,
                    steamplayer.personastate,
                    steamplayer.realname,
                    steamplayer.timecreated,
                    steamplayer.loccountrycode,
                    steamplayer.locstatecode,
                    steamplayer.loccityid,
                    now,
                ),
            )
        except Exception as err:
            logger.critical(err)
            raise
        Database().connection.commit()

        #
        return steamplayer

    def _get_player_summaries(self, steamids):

        if not self._webapi:
            return []

        jdoc = self._webapi.call(
            "ISteamUser.GetPlayerSummaries", steamids=",".join([str(x.as_64) for x in steamids])
        )

        return list(jdoc["response"]["players"])
