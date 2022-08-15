"""Table of `SteamPlayer`s."""

import contextlib
import time

from tf2mon.database import Base, Column, Integer, NoResultFound, Session, String, select
from tf2mon.steamid import BOT_STEAMID, SteamID


class SteamPlayer(Base):
    """Represent ['response']['players'] element from `ISteamUser.GetPlayerSummaries`."""

    __tablename__ = "steamplayers"

    steamid = Column(Integer, primary_key=True)
    personaname = Column(String)
    profileurl = Column(String)
    personastate = Column(String)
    realname = Column(String)
    timecreated = Column(Integer)
    loccountrycode = Column(String)
    locstatecode = Column(String)
    loccityid = Column(String)
    mtime = Column(Integer)

    _age = None

    def __init__(self, steamid: int):
        """Initialize `SteamPlayer` with primary key `steamid`."""

        self.steamid = steamid

    def setattrs(self, attrs) -> None:
        """Docstring."""

        for attr in attrs:
            setattr(self, attr, attr)

    def update(self, summary: dict[str, ...]) -> None:
        """Update properties from dict."""

        for key in [
            "personaname",
            "profileurl",
            "personastate",
            "realname",
            "timecreated",
            "loccountrycode",
            "locstatecode",
            "loccityid",
            "mtime",
        ]:
            setattr(self, key, summary.get(key))

    @staticmethod
    def find_steamid(steamid: SteamID) -> "SteamPlayer":
        """Lookup and return `SteamPlayer` with matching `steamid`."""

        stmt = select(SteamPlayer).where(SteamPlayer.steamid == steamid.id)
        result = Session().scalars(stmt)
        steamplayer = None
        with contextlib.suppress(NoResultFound):
            steamplayer = result.one()
        return steamplayer

    @property
    def age(self) -> str:
        """Docstring."""

        if self._age is None:
            self._age = (int(time.time()) - self.timecreated) // 86400 if self.timecreated else 0
        return self._age

    @property
    def is_gamebot(self) -> bool:
        """Docstring."""

        return self.steamid == BOT_STEAMID
