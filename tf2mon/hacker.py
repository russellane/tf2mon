"""Represent milenko's playerlist.

See https://raw.githubusercontent.com/PazerOP/tf2_bot_detector/master/schemas/v3/playerlist.schema.json
"""  # noqa

import csv
import json
import time
from collections import defaultdict
from enum import Enum
from pathlib import Path

import steam.steamid
from loguru import logger

from tf2mon.steamplayer import SteamPlayer


class HackerAttr(Enum):
    """Valid Hacker Attributes."""

    # milenko's values
    CHEATER = "cheater"
    SUSPECT = "suspect"
    EXPLOITER = "exploiter"
    RACIST = "racist"
    # tf2mon's additional values
    MILENKO = "milenko"  # track milenko's bot-hunting bots
    GAMEBOT = "bot"  # legitimate gamebot; eg `Numnutz`


class DBTYPE(Enum):
    """Valid database types."""

    BASE = "base"  # milenko's database
    LOCAL = "local"  # local addendums


class Hacker:
    """Example from milenko's playerlist.

    "players": [
        {
            "attributes": [
                "cheater"
            ],
            "last_seen": {
                "player_name": "enzic2",
                "time": 1593821733
            },
            "steamid": "[U:1:1254884]"
        },

    Hackers in tf2mon's list have additional properties:
        {

            "names": [],
        }
    """

    def __init__(
        self,
        json_player=None,
        dbtype: DBTYPE = None,
        steamid=None,
        attribute=None,
        name=None,
    ):
        """Create Hacker.

        Create Hacker either from json record, or the given values.
        The json record may be from milenko's file or a local file. Loose
        values are given when we insert a new hacker. The json record and
        the loose values are mutually exclusive, and one of them is
        required.
        """

        # pylint: disable=too-many-arguments

        if json_player:
            assert steamid is attribute is name is None
            self._from_json(json_player)
            assert dbtype in DBTYPE
            self.dbtype = dbtype
        else:
            assert steamid
            assert attribute
            assert name
            self.steamid = steamid
            self.attributes = [HackerAttr(attribute)]
            self.names = [name]
            self.last_name_seen = name
            self.last_time_seen = int(time.time())
            assert dbtype in (None, DBTYPE.LOCAL)
            self.dbtype = DBTYPE.LOCAL

    def _from_json(self, jdoc):

        # required: unique id
        self.steamid = steam.steamid.SteamID(jdoc["steamid"])

        # required: type of hacker
        self.attributes = [HackerAttr(x) for x in jdoc["attributes"]]

        # optional tf2mon extension: names this hacker has used
        self.names = jdoc.get("names", [])
        self.last_name_seen = None
        self.last_time_seen = 0

        # optional: previous appearance
        if last_seen := jdoc.get("last_seen"):
            # optional
            if name := last_seen.get("player_name"):
                if name not in self.names:
                    self.names.append(name)
                self.last_name_seen = name
            # required
            self.last_time_seen = last_seen["time"]

    @property
    def is_suspect(self):
        """Return True if hacker is suspect."""
        return HackerAttr.SUSPECT in self.attributes

    @property
    def is_racist(self):
        """Return True if hacker is racist."""
        return HackerAttr.RACIST in self.attributes

    @property
    def is_milenko(self):
        """Return True if hacker is milenko."""
        return HackerAttr.MILENKO in self.attributes

    @property
    def is_gamebot(self):
        """Return True if player is a legitimate gamebot."""
        return HackerAttr.GAMEBOT in self.attributes

    @property
    def is_banned(self):
        """Return True if hacker is suspect or racist."""
        return HackerAttr.CHEATER in self.attributes or HackerAttr.RACIST in self.attributes

    def attributes_to_str(self):
        """Return a displayable representation of the attributes."""

        return ",".join([x.value for x in self.attributes])

    def __repr__(self):
        return str(self.__dict__)

    def to_json(self):
        """Return json document for this `Hacker`."""

        jdoc = {"attributes": [x.value for x in self.attributes]}
        if self.last_time_seen:
            last_seen = jdoc["last_seen"] = {}
            if self.last_name_seen:
                last_seen["player_name"] = self.last_name_seen
            last_seen["time"] = self.last_time_seen
        jdoc["steamid"] = self.steamid.id
        if self.names:
            jdoc["names"] = self.names
        return jdoc

    def track_appearance(self, name):
        """Record user appearing as given name."""

        if name not in self.names:
            logger.warning(f"adding name {name!r}")
            self.names.append(name)

        self.last_name_seen = name
        self.last_time_seen = int(time.time())
        logger.warning(f"time {self.last_time_seen} name {self.last_name_seen!r}")


class HackerManager:
    """Collection of `Hacker`s."""

    def __init__(self, *, base: Path = None, local: Path = None):
        """Connect to `Hacker` database.

        Load records from `base`, and overlay with records from
        `local`. Save `local_path` for `save_database` to use, and
        make the records accessible via `lookup_steamid`.
        """

        self._hackers_by_steamid = {}
        if base:
            self._load(base, DBTYPE.BASE)  # load the base list
        if local:
            self._load(local, DBTYPE.LOCAL)  # merge our addendums

        # self._base = base        # we only read from this file
        self._path_local = local  # we will write to this file

        # for `lookup_name`
        self._hackers_by_name = defaultdict(list)
        for hacker in self._hackers_by_steamid.values():
            for name in hacker.names:
                self._hackers_by_name[name].append(hacker)

    def _load(self, path: Path, dbtype: DBTYPE):
        """Read playerlist at `path` loading `Hacker`s into collection."""

        logger.info(f"Reading `{path}`")
        with open(path, encoding="utf-8") as file:
            for json_player in json.load(file)["players"]:
                hacker = Hacker(json_player, dbtype)
                self._hackers_by_steamid[hacker.steamid] = hacker

    def save_database(self):
        """Save LOCAL database to disk."""

        logger.info(f"Writing {self._path_local}")
        jdoc = {
            "players": [
                x.to_json()
                for x in self._hackers_by_steamid.values()
                if x.dbtype == DBTYPE.LOCAL
            ]
        }
        with open(self._path_local, "w", encoding="utf-8") as file:
            json.dump(jdoc, file, indent=4)
            print("", file=file)

    def lookup_name(self, name):
        """Return `Hacker` for given name, else None if not found."""

        logger.trace(f"name {name}")
        return self._hackers_by_name.get(name)

    def lookup_steamid(self, steamid):
        """Return `Hacker` for given steamid, else None if not found."""

        logger.trace(f"steamid {steamid}")
        return self._hackers_by_steamid.get(steamid)

    def add(self, steamid, attribute, name):
        """Create new `Hacker`, add to LOCAL database, return new `Hacker`."""

        hacker = Hacker(steamid=steamid, attribute=attribute, name=name)
        self._hackers_by_steamid[hacker.steamid] = hacker
        self._hackers_by_name[name].append(hacker)
        return hacker

    def load_gamebots(self, path):
        """Read and create `GAMEBOT`s from list of names read from `path`.

        Used by qvalve; not used by tf2mon.
        """

        steamid = steam.steamid.SteamID(SteamPlayer.BOT_S_STEAMID)

        with open(path, encoding="utf-8") as file:
            for (name,) in csv.reader(file):
                self.add(steamid, HackerAttr.GAMEBOT, name)
