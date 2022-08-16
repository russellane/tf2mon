"""Table of `Player`s."""

import json
import time
from dataclasses import dataclass

from loguru import logger

from tf2mon.database import Database, DatabaseTable


@dataclass
class Player(DatabaseTable):
    """A `Player`."""

    # pylint: disable=too-many-instance-attributes

    __tablename__ = "players"

    # database columns
    steamid: int  # primary key

    # defcon6
    bot: str = ""
    friends: str = ""
    tacobot: str = ""
    pazer: str = ""

    # playerlist.official
    _cheater: str = ""
    _suspect: str = ""
    _exploiter: str = ""
    _racist: str = ""
    _last_name: str = ""
    _s_last_time: str = ""

    # tf2mon
    cheater: str = ""
    suspect: str = ""
    exploiter: str = ""
    racist: str = ""
    milenko: str = ""
    last_name: str = ""
    s_last_time: str = ""
    names: str = ""

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

    def setattrs(self, attrs) -> None:
        """Docstring."""
        for attr in attrs:
            setattr(self, attr, attr)

    @classmethod
    def select_all(cls) -> list["Player"]:
        """Yield all `Player`s in database."""

        for row in Database().execute(f"select * from {cls.__tablename__}"):
            yield cls(*tuple(row))

    @classmethod
    def lookup_steamid(cls, steamid: int) -> "Player":
        """Return `Player` for given steamid, else None if not found."""

        Database().execute(f"select * from {cls.__tablename__} where steamid=?", (steamid,))
        if row := Database().fetchone():
            return cls(*tuple(row))
        return None

    def upsert(self) -> None:
        """Update or Insert this row into the table."""

        try:
            Database().execute(
                f"replace into {self.__tablename__} {self.valueholders()}",
                self.astuple(),
            )
        except Exception as err:
            logger.critical(err)
            raise
        Database().connection.commit()

    def track_appearance(self, name):
        """Record user appearing as given name."""

        self.last_name = name
        self.s_last_time = self.strftime()
        logger.warning(f"time {self.s_last_time} name {self.last_name!r}")

        logger.warning(f"self.names {self.names!r}")
        names = json.loads(self.names).get("json", []) if self.names else []
        logger.warning(f"names {names!r}")
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
