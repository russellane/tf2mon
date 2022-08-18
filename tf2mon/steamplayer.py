"""Table of `SteamPlayer`s."""

import time
from dataclasses import dataclass

from tf2mon.database import Database, DatabaseTable
from tf2mon.steamid import BOT_STEAMID, SteamID


@dataclass
class SteamPlayer(DatabaseTable):
    """Represent ['response']['players'] element from `ISteamUser.GetPlayerSummaries`."""

    # pylint: disable=too-many-instance-attributes

    __tablename__ = "steamplayers"

    # database columns
    steamid: int  # primary key
    personaname: str = ""
    profileurl: str = ""
    personastate: int = 0
    realname: str = ""
    timecreated: int = 0
    loccountrycode: str = ""
    locstatecode: str = ""
    loccityid: str = ""
    mtime: int = 0

    def __post_init__(self):

        steamid = SteamID(self.steamid)
        if self.profileurl and self.profileurl == steamid.community_url + "/":
            # for asthetics only; to avoid clutter
            self.profileurl = None  # indicate long noisy determinable value

        now = int(time.time())

        self.age = 0  # number of days since account was created.
        if self.timecreated:
            self.age = (now - self.timecreated) // 86400
        self.mtime = self.mtime or now

    @classmethod
    def create_table(cls) -> None:
        """Execute create table statement."""

        Database().execute(
            f"create table if not exists {cls.__tablename__}"
            """(
                steamid integer primary key,
                personaname text,
                profileurl text,
                personastate integer,
                realname text,
                timecreated integer,
                loccountrycode text,
                locstatecode text,
                loccityid text,
                mtime integer
            )""",
        )
        Database().connection.commit()

    @classmethod
    def fetch_steamid(cls, steamid: int) -> "SteamPlayer":
        """Return `SteamPlayer` for given steamid, else None if not found."""

        Database().execute(f"select * from {cls.__tablename__} where steamid=?", (steamid,))
        if row := Database().fetchone():
            return cls(*tuple(row))
        return None

    @property
    def is_gamebot(self) -> bool:
        """Return True if this is a legitimate game BOT; not a hacker."""

        return self.steamid == BOT_STEAMID.id
