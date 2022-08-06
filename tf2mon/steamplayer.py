"""Table of `SteamPlayer`s."""

import time

from tf2mon.database import Base, Column, Integer, String
from tf2mon.steamid import BOT_STEAMID


class SteamPlayer(Base):
    """Represent an ['response']['players'] element from `ISteamUser.GetPlayerSummaries`."""

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
