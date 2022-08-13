"""Table of `Player`s."""

import contextlib
import json
import time

from loguru import logger

from tf2mon.database import Base, Column, Integer, NoResultFound, Session, String, select


class Player(Base):
    """A `Player`."""

    __tablename__ = "players"

    # key
    steamid = Column(Integer, primary_key=True)

    # defcon6
    bot = Column(String)
    friends = Column(String)
    tacobot = Column(String)
    pazer = Column(String)

    # playerlist.official
    _cheater = Column(String)
    _suspect = Column(String)
    _exploiter = Column(String)
    _racist = Column(String)
    _last_name = Column(String)
    _s_last_time = Column(String)

    # tf2mon
    cheater = Column(String)
    suspect = Column(String)
    exploiter = Column(String)
    racist = Column(String)
    milenko = Column(Integer)
    last_name = Column(String)
    s_last_time = Column(String)
    names = Column(String)

    # Attributes.
    # base
    CHEATER = "cheater"
    SUSPECT = "suspect"
    EXPLOITER = "exploiter"
    RACIST = "racist"
    # tf2mon
    MILENKO = "milenko"
    GAMEBOT = "gamebot"
    # defcon6
    BOT = "bot"
    FRIENDS = "friends"
    TACOBOT = "tacobot"
    PAZER = "pazer"

    def __init__(self, steamid: int):
        """Initialize `Player` with primary key `steamid`."""

        self.steamid = steamid

    def setattrs(self, attrs) -> None:
        """Docstring."""
        for attr in attrs:
            setattr(self, attr, attr)

    @staticmethod
    def lookup_steamid(steamid: int) -> "Player":
        """Return `Player` for given steamid, else None if not found."""

        stmt = select(Player).where(Player.steamid == steamid)
        result = Session().scalars(stmt)
        player = None
        with contextlib.suppress(NoResultFound):
            player = result.one()
        return player

    @classmethod
    def add(cls, steamid: int, attrs: list[str], name: str) -> "Player":
        """Add and return new `Player`."""

        player = cls(steamid)
        player.setattrs(attrs)
        player.track_appearance(name)
        Session().add(player)
        return player

    def track_appearance(self, name):
        """Record user appearing as given name."""

        self.last_name = name
        self.s_last_time = self.strftime()
        logger.warning(f"time {self.s_last_time} name {self.last_name!r}")

        names = json.loads(self.names).get("json", []) if self.names else []
        if name not in names:
            logger.warning(f"adding name {name!r}")
            names.append(name)
        self.names = json.dumps({"json": names})

    def strftime(self, seconds=None) -> str:
        """Return time formatted as a string."""

        return time.strftime("%FT%T", time.localtime(seconds or int(time.time())))

    @property
    def display_level(self) -> str:
        """Return logging level for displaying this player."""

        # pylint: disable=too-many-return-statements

        # Ordered.
        if self.racist or self._racist:
            return "RACIST"
        if self.cheater or self._cheater:
            return "CHEATER"
        if self.suspect or self._suspect:
            return "SUSPECT"
        if self.exploiter or self._exploiter:
            return "EXPLOITER"
        if self.milenko:
            return "MILENKO"
        if self.bot:
            return "BOT"
        if self.friends:
            return "FRIENDS"
        if self.tacobot:
            return "TACOBOT"
        if self.pazer:
            return "PAZER"

        logger.error("unknown attributes")
        return self.__class__.__name__

    @property
    def is_banned(self):
        """Return True if hacker is suspect or racist."""

        return (
            self.racist
            or self._racist
            or self.cheater
            or self._cheater
            or self.exploiter
            or self._exploiter
            or self.bot
            or self.friends
            or self.tacobot
            or self.pazer
        )


# DEFCON6 = [
#     HackerAttr.BOT,
#     HackerAttr.FRIENDS,
#     HackerAttr.TACOBOT,
#     HackerAttr.PAZER,
# ]
# BANNED = [
#     HackerAttr.CHEATER,
#     HackerAttr.RACIST,
# ] + DEFCON6
