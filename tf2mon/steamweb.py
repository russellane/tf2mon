"""Interface to `ISteamUser.GetPlayerSummaries`."""

import time

import steam.webapi
from loguru import logger

from tf2mon.database import NoResultFound, Session, select
from tf2mon.steamid import BOT_STEAMID
from tf2mon.steamplayer import SteamPlayer

MAX_AGE = 2 * 60 * 60


class SteamWebAPI:
    """Interface to `ISteamUser.GetPlayerSummaries`.

    Results are cached to avoid banging the server.
    """

    def __init__(self, webapi_key):
        """Initialize interface."""

        if webapi_key:
            self._webapi = steam.webapi.WebAPI(key=webapi_key)
        else:
            self._webapi = None
            logger.warning("Running without `webapi_key`")

        self._nbots = 0

    def find_steamid(self, steamid) -> object:
        """Lookup and return `SteamPlayer` with matching `steamid`.

        Always returns a `SteamPlayer` object, even for invalid steamids.

        Use web service to get "Player Summary" of given `steamid`.
        Create dummy object for game bots.
        """

        now = int(time.time())

        if steamid == BOT_STEAMID:
            return self._create_gamebot(steamid, now)

        if not steamid.is_valid():
            return self._create_invalid(steamid, now)

        # check cache.
        session = Session()
        stmt = select(SteamPlayer).where(SteamPlayer.steamid == steamid.id)
        result = session.scalars(stmt)
        try:
            steamplayer = result.one()
        except NoResultFound:
            # logger.debug('notfound')
            steamplayer = None

        if steamplayer and steamplayer.mtime > now - MAX_AGE:
            # logger.debug('current')
            return steamplayer
        # if steamplayer:
        #     logger.debug('expired')

        # not current or not in cache; call web service.
        player_summaries = self._get_player_summaries([steamid])
        if len(player_summaries) != 1:
            return self._create_invalid(steamid, now)
        jplayer = player_summaries[0]

        # update cache.
        if not steamplayer:
            steamplayer = SteamPlayer()
            steamplayer.steamid = steamid.id
            new = True
        else:
            new = False

        # for key, value in jplayer.items():
        #     setattr(steamplayer, key, value)
        steamplayer.personaname = jplayer.get("personaname")
        steamplayer.profileurl = jplayer.get("profileurl")
        steamplayer.personastate = jplayer.get("personastate")
        steamplayer.realname = jplayer.get("realname")
        steamplayer.timecreated = jplayer.get("timecreated")
        steamplayer.loccountrycode = jplayer.get("loccountrycode")
        steamplayer.locstatecode = jplayer.get("locstatecode")
        steamplayer.loccityid = jplayer.get("loccityid")
        steamplayer.mtime = now

        if new:
            session.add(steamplayer)
        session.commit()

        #
        return steamplayer

    def _create_gamebot(self, steamid, now) -> SteamPlayer:
        """Create and return a gamebot."""

        self._nbots += 1
        steamplayer = SteamPlayer()
        steamplayer.steamid = steamid.id
        steamplayer.personaname = ""
        steamplayer.profileurl = ""
        steamplayer.personastate = 0
        steamplayer.realname = ""
        steamplayer.timecreated = now - (self._nbots * 86400)
        steamplayer.loccountrycode = "US"
        steamplayer.locstatecode = "IL"
        steamplayer.loccityid = "CHGO"
        steamplayer.mtime = now
        return steamplayer

    def _create_invalid(self, steamid, now) -> SteamPlayer:
        """Create and return a dummy."""

        steamplayer = SteamPlayer()
        steamplayer.steamid = steamid.id
        steamplayer.personaname = "?"
        steamplayer.profileurl = "?"
        steamplayer.personastate = 0
        steamplayer.realname = "?"
        steamplayer.timecreated = now
        steamplayer.loccountrycode = "?"
        steamplayer.locstatecode = "?"
        steamplayer.loccityid = "?"
        steamplayer.mtime = now
        return steamplayer

    def _get_player_summaries(self, steamids):

        if not self._webapi:
            return []

        jdoc = self._webapi.call(
            "ISteamUser.GetPlayerSummaries", steamids=",".join([str(x.as_64) for x in steamids])
        )

        return list(jdoc["response"]["players"])
