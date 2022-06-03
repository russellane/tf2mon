"""Interface to `ISteamUser.GetPlayerSummaries`."""

import sqlite3
import time

import steam.steamid
import steam.webapi
from loguru import logger

from tf2mon.steamplayer import SteamPlayer


class SteamWebAPI:
    """Interface to `ISteamUser.GetPlayerSummaries`.

    Results are cached to avoid banging the server.
    """

    def __init__(self, webapi_key, dbpath, max_age=2 * 60 * 60):
        """Initialize interface to Steam_Web_API.

        The interface cannot be used until `connect` is called.
        """

        #
        self._webapi_key = webapi_key
        self._webapi = steam.webapi.WebAPI(key=self._webapi_key)

        #
        self._dbpath = dbpath
        self._max_age = max_age
        self._con = None  # set in `connect`.
        self._cur = None  # set in `connect`.

        #
        self._nbots = 0  # incremented by `find_steamid`.

    def connect(self):
        """Prepare to use interface to Steam_Web_API.

        This step is separate from the constructor to allow connecting from
        a different thread.
        """

        logger.debug(f"connecting to sqlite3 at `{self._dbpath}`")
        self._con = sqlite3.connect(self._dbpath)
        self._con.row_factory = sqlite3.Row
        self._cur = self._con.cursor()

        self._cur.execute(
            """create table if not exists steamplayers(
                steamid integer primary key,
                personaname text,
                profileurl text,
                personastate text,
                realname text,
                timecreated integer,
                loccountrycode text,
                locstatecode text,
                loccityid text,
                mtime integer)"""
        )

        self._con.commit()

    def find_steamid(self, steamid):
        """Lookup and return `SteamPlayer` with matching `steamid`.

        Use web service to get "Player Summary" of given `steamid`.
        Create dummy object for game bots.

        Args:
            steamid: `steam.steamid.SteamID` of user to find.
        """

        if steamid.id == int(SteamPlayer.BOT_S_STEAMID):
            # create a dummy steamid for this bot; (not a hacker, a real game bot)
            self._nbots += 1
            return SteamPlayer(
                {
                    "steamid": steamid.id,
                    "personaname": None,
                    "profileurl": "",
                    "personastate": 0,
                    "realname": "",
                    "timecreated": int(time.time()) - (self._nbots * 86400),
                    "loccountrycode": "US",
                    "locstatecode": "IL",
                    "loccityid": "CHGO",
                }
            )

        # it's not a game bot; look in database.
        try:
            self._cur.execute("select * from steamplayers where steamid=?", (steamid.id,))
        except Exception as err:
            logger.critical(err)
            raise
        #
        if row := self._cur.fetchone():
            # convert tuple-like sqlite3.Row to json document
            steamplayer = SteamPlayer({k: row[k] for k in row.keys()})
            if steamplayer.mtime > int(time.time()) - self._max_age:
                # logger.debug('current')
                return steamplayer
            # logger.debug('expired')
        # else:
        #    logger.debug('notfound')

        # not current or not in database; ping server.
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
                    "timecreated": int(time.time()),
                    "loccountrycode": "",
                    "locstatecode": "",
                    "loccityid": "",
                }
            )

        # construct.
        steamplayer = SteamPlayer(player_summaries[0])

        # update database.
        try:
            self._cur.execute(
                "replace into steamplayers values(?,?,?,?,?,?,?,?,?,?)",
                (
                    steamplayer.steamid.id,
                    steamplayer.personaname,
                    steamplayer.profileurl,
                    steamplayer.personastate,
                    steamplayer.realname,
                    steamplayer.timecreated,
                    steamplayer.loccountrycode,
                    steamplayer.locstatecode,
                    steamplayer.loccityid,
                    int(time.time()),
                ),
            )
        except Exception as err:
            logger.critical(err)
            raise
        self._con.commit()

        #
        return steamplayer

    def _get_player_summaries(self, steamids):

        jdoc = self._webapi.call(
            "ISteamUser.GetPlayerSummaries", steamids=",".join([str(x.as_64) for x in steamids])
        )

        return list(jdoc["response"]["players"])
