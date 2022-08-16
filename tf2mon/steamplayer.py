"""Table of `SteamPlayer`s."""

import time
from dataclasses import InitVar, dataclass, field

from tf2mon.database import Database
from tf2mon.steamid import BOT_STEAMID, SteamID


@dataclass
class SteamPlayer:
    """Represent ['response']['players'] element from `ISteamUser.GetPlayerSummaries`."""

    # pylint: disable=too-many-instance-attributes

    jdoc: InitVar[str]  # ['response']['players'] element

    # database columns
    steamid: int = field(default=None, init=False)  # primary key
    personaname: str = field(default="", init=False)
    profileurl: str = field(default="", init=False)
    personastate: str = field(default="", init=False)
    realname: str = field(default="", init=False)
    timecreated: int = field(default=None, init=False)
    loccountrycode: str = field(default="", init=False)
    locstatecode: str = field(default="", init=False)
    loccityid: str = field(default="", init=False)
    mtime: int = field(default=None, init=False)

    # additional (non-database) properties
    age: int = field(default=None, init=False)

    def __post_init__(self, jdoc: dict[str, ...]):
        """Init `SteamPlayer` from json document.

        Args:
            jdoc:   `['response']['players']` element returned by
                    `ISteamUser.GetPlayerSummaries`.
        """

        steamid = SteamID(jdoc.get("steamid"))
        self.steamid = steamid.id
        self.personaname = jdoc.get("personaname")
        self.profileurl = jdoc.get("profileurl")
        self.personastate = jdoc.get("personastate")
        self.realname = jdoc.get("realname")
        self.timecreated = jdoc.get("timecreated")
        self.loccountrycode = jdoc.get("loccountrycode")
        self.locstatecode = jdoc.get("locstatecode")
        self.loccityid = jdoc.get("loccityid")

        #
        if self.profileurl and self.profileurl == steamid.community_url + "/":
            # for asthetics only; to avoid clutter
            self.profileurl = None  # indicate long noisy determinable value

        now = int(time.time())
        if self.timecreated:
            self.age = (now - self.timecreated) // 86400
        self.mtime = jdoc.get("mtime", now)

    @staticmethod
    def select_all() -> list["SteamPlayer"]:
        """Return list of all `SteamPlayer`s in database."""

        for row in Database().execute("select * from steamplayers"):
            yield SteamPlayer(dict(row))
            # yield SteamPlayer({k: row[k] for k in row.keys()})

    @staticmethod
    def find_steamid(steamid: SteamID) -> "SteamPlayer":
        """Lookup and return `SteamPlayer` with matching `steamid`."""

        Database().execute("select * from steamplayers where steamid=?", (steamid.id,))
        if row := Database().fetchone():
            # convert tuple-like sqlite3.Row to json document
            return SteamPlayer({k: row[k] for k in row.keys()})
        return None

    @property
    def is_gamebot(self) -> bool:
        """Return True if this is a legitimate game BOT; not a hacker."""

        return self.steamid == BOT_STEAMID

    def create_table(self) -> None:
        """Execute create table statement."""

        Database().execute(
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
        Database().connection.commit()
