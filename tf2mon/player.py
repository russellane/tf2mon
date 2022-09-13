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

    def __post_init__(self):
        # additional (non-database) properties

        self._s_prev_time = self._s_last_time
        self.s_prev_time = self.s_last_time

    @classmethod
    def create_table(cls) -> None:
        """Execute create table statement."""

        Database().execute(
            f"create table if not exists {cls.__tablename__}"
            """(
                steamid integer primary key,
                bot text,
                friends text,
                tacobot text,
                pazer text,
                _cheater text,
                _suspect text,
                _exploiter text,
                _racist text,
                _last_name text,
                _s_last_time text,
                cheater text,
                suspect text,
                exploiter text,
                racist text,
                milenko text,
                last_name text,
                s_last_time text,
                names text
            )""",
        )
        Database().connection.commit()

    def getattrs(self) -> list[str]:
        """Docstring."""

        return [
            self.bot,
            self.friends,
            self.tacobot,
            self.pazer,
            self._cheater,
            self._suspect,
            self._exploiter,
            self._racist,
            self._last_name,
            self._s_last_time,
            self.cheater,
            self.suspect,
            self.exploiter,
            self.racist,
            self.milenko,
        ]

    def setattrs(self, attrs) -> None:
        """Docstring."""
        for attr in attrs:
            setattr(self, attr, attr)

    @classmethod
    def fetch_steamid(cls, steamid: int) -> "Player":
        """Return `Player` for given steamid, else None if not found."""

        Database().execute(f"select * from {cls.__tablename__} where steamid=?", (steamid,))
        if row := Database().fetchone():
            return cls(*tuple(row))
        return None

    def track_appearance(self, name: str) -> None:
        """Record user appearing as given name."""

        level = self.display_level
        leader = f"{level}: {self.steamid}"

        logger.log(level, f"{leader}: name: `{name}`")
        logger.log(level, f"{leader}: last={self.s_last_time} {self._s_last_time}")

        self._s_prev_time = self._s_last_time
        self.s_prev_time = self.s_last_time
        self.s_last_time = self.strftime()

        aliases = list(self.aliases)  # deserialize

        if self.last_name not in aliases:
            logger.log(level, f"{leader}: adding last_name `{self.last_name}`")
            aliases.append(self.last_name)
        self.last_name = name

        if name not in aliases:
            logger.log(level, f"{leader}: adding alias `{name}`")
            aliases.append(name)

        self.names = json.dumps({"json": aliases})  # serialize
        self.upsert()

    @property
    def aliases(self) -> str:
        """Return list of names used by this account."""

        return json.loads(self.names).get("json", []) if self.names else []

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
            # or self.pazer
        )

    @staticmethod
    def new_player(steamid: int, attrs: list[str], name: str) -> "Player":
        """Create, insert and return new `Player`."""

        player = Player(steamid)
        player.setattrs(attrs)
        player.track_appearance(name)
        return player
