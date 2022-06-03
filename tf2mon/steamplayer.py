"""Wrapper for `ISteamUser.GetPlayerSummaries`.

See https://developer.valvesoftware.com/wiki/Steam_Web_API
"""
import time

import humanize
import steam.steamid
from loguru import logger


class SteamPlayer:
    """Represent an ['response']['players'] element from `ISteamUser.GetPlayerSummaries`."""

    # pylint: disable=too-many-instance-attributes

    BOT_NAME = "BOT"
    BOT_S_STEAMID = "1"
    BOT_STEAMID = int(BOT_S_STEAMID)

    def __init__(self, jdoc):
        """Create `SteamPlayer` from json document.

        Args:
            jdoc:   `['response']['players']` element returned by
                    `ISteamUser.GetPlayerSummaries`.
        """

        self.steamid = steam.steamid.SteamID(jdoc.get("steamid"))
        self.personaname = jdoc.get("personaname")
        self.profileurl = jdoc.get("profileurl")
        self.personastate = jdoc.get("personastate")
        self.realname = jdoc.get("realname")
        self.timecreated = jdoc.get("timecreated")
        self.loccountrycode = jdoc.get("loccountrycode")
        self.locstatecode = jdoc.get("locstatecode")
        self.loccityid = jdoc.get("loccityid")

        #
        if self.profileurl and self.profileurl == self.steamid.community_url + "/":
            # for asthetics only; to avoid clutter
            self.profileurl = None  # indicate long noisy determinable value

        #
        if not self.timecreated:
            logger.warning(f"no timecreated {str(self.__dict__)}")

        now = int(time.time())
        self.age = humanize.naturaldelta(now - self.timecreated) if self.timecreated else ""
        self.mtime = jdoc.get("mtime", now)

    def __repr__(self):
        return str(self.__dict__)

    @property
    def is_legitimate_game_bot(self):
        """Return True if this is a legitimate game BOT; not a hacker."""

        return self.steamid.id == self.BOT_STEAMID


def steamid_from_str(s_steamid):
    """Return `steam.steamid.SteamID` from string in STATUS and LOBBY lines.

    Return None if invalid.

    Args:
        s_steamid: string, decimal number or "BOT".
    """

    if s_steamid == SteamPlayer.BOT_NAME:
        # create a dummy steamid for this bot; (not a hacker, a real game bot)
        s_steamid = SteamPlayer.BOT_S_STEAMID

    steamid = steam.steamid.SteamID(s_steamid)
    if not steamid.is_valid():
        logger.error(f"invalid steamid {s_steamid}")
        return None

    return steamid
