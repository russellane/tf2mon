"""Docstring."""

from loguru import logger
from steam.steamid import SteamID

BOT_STEAMID = SteamID(1)


def parse_steamid(s_steamid: str) -> SteamID:
    """Parse and return `SteamID` from STATUS and LOBBY lines.

    Return `None` if invalid, or `BOT_STEAMID` if gamebot.
    """

    if s_steamid == "BOT":
        return BOT_STEAMID

    steamid = SteamID(s_steamid)
    if not steamid.is_valid():
        logger.error(f"invalid steamid {s_steamid}")
        return None

    return steamid
