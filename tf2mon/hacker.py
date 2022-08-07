"""Hacker database."""

import csv
import json
import time
from enum import Enum
from pathlib import Path

from loguru import logger

from tf2mon.steamid import BOT_STEAMID, SteamID
from tf2mon.texttable import TextColumn, TextTable

JsonType = dict[str, object]


class HackerAttr(Enum):
    """Valid Hacker Attributes."""

    # base values
    CHEATER = "cheater"
    SUSPECT = "suspect"
    EXPLOITER = "exploiter"
    RACIST = "racist"
    # tf2mon's additional values
    MILENKO = "milenko"  # track milenko's bot-hunting bots
    GAMEBOT = "gamebot"  # legitimate gamebot; eg `Numnutz`
    # defcon6
    BOT = "bot"
    FRIENDS = "friends"
    TACOBOT = "tacobot"
    PAZER = "pazer"


DEFCON6 = [
    HackerAttr.BOT,
    HackerAttr.FRIENDS,
    HackerAttr.TACOBOT,
    HackerAttr.PAZER,
]

BANNED = [
    HackerAttr.CHEATER,
    HackerAttr.RACIST,
] + DEFCON6


FMT_TIME = "%FT%T"


class Hacker:
    """Example record from upstream file.

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

    We add additional properties:
        {
            "last_seen": {
                "time_string": "mm-dd-yy hh:mm:ss",
            },
            "names": [],
        }
    """

    def __init__(self, player: JsonType):
        """Init `Hacker` from `player`."""

        # required: unique id
        self.steamid = SteamID(player["steamid"])

        # required: type of hacker
        self.attributes = [HackerAttr(x) for x in player["attributes"]]

        # optional tf2mon extension: names this hacker has used
        self.names = player.get("names", [])
        self.last_name = None
        self.last_time = 0
        # optional tf2mon extension: last_time as string
        self.s_last_time = None

        # optional: previous appearance
        if last_seen := player.get("last_seen"):
            if name := last_seen.get("player_name"):
                if name not in self.names:
                    self.names.append(name)
                self.last_name = name
            self.last_time = last_seen["time"]
            self.s_last_time = last_seen.get(
                "time_string",
                time.strftime(
                    FMT_TIME,
                    time.localtime(self.last_time),
                ),
            )

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

        return any([x for x in self.attributes if x in BANNED])  # noqa

    @property
    def is_defcon6(self):
        """Return True if hacker has a defcon6 attribute."""

        return any([x for x in self.attributes if x in DEFCON6])  # noqa

    def __repr__(self):
        return str(self.__dict__)

    @property
    def as_json(self) -> JsonType:
        """Return json `player` record for this `Hacker`."""

        player = {"attributes": [x.value for x in self.attributes]}
        if self.last_time:
            player["last_seen"] = {}
            if self.last_name:
                player["last_seen"]["player_name"] = self.last_name
            player["last_seen"]["time"] = self.last_time
            player["last_seen"]["time_string"] = self.s_last_time
        player["steamid"] = self.steamid.as_steam3
        if self.names:
            player["names"] = self.names
        return player

    def track_appearance(self, name):
        """Record user appearing as given name."""

        if name not in self.names:
            logger.warning(f"adding name {name!r}")
            self.names.append(name)

        self.last_name = name
        self.last_time = int(time.time())
        self.s_last_time = time.strftime(FMT_TIME, time.localtime(self.last_time))
        logger.warning(f"time {self.s_last_time} name {self.last_name!r}")


class HackerManager:
    """Collection of `Hacker`s."""

    def __init__(self, path: Path):
        """Read `Hacker` database at `path`."""

        self._path = path
        self._hackers_by_steamid: dict[SteamID, Hacker] = {}
        self.load(self._path)

    def __call__(self) -> dict[SteamID, Hacker]:
        """Return map of steamids to hackers."""

        return self._hackers_by_steamid

    def load(self, path: Path):
        """Merge database at `path` into this database."""

        msg = f"`--hackers` database at `{path}`"
        if not self._path.exists():
            logger.warning(f"Missing {msg}")
            return

        logger.info(f"Reading {msg}")
        with open(path, encoding="utf-8") as file:
            try:
                jdoc = json.load(file)
            except json.decoder.JSONDecodeError as err:
                logger.error(f"{err} in {msg}")
                return

        for player in jdoc.get("players"):
            #
            hacker = Hacker(player)

            if cached := self._hackers_by_steamid.get(hacker.steamid):
                logger.warning(f"Merging steamid `{hacker.steamid.id}")
                # Merge attributes and names; keep latest time.

                for attr in hacker.attributes:
                    logger.debug(f"HATTR {attr.value}")

                for attr in cached.attributes:
                    if attr not in hacker.attributes:
                        hacker.attributes.append(attr)
                        logger.debug(f"CATTR {attr.value}")

                for name in hacker.names:
                    logger.debug("HNAME " + name.replace("\n", "."))

                for name in cached.names:
                    if name not in hacker.names:
                        hacker.names.append(name)
                        logger.debug("CNAME " + name.replace("\n", "."))

                if hacker.last_time < cached.last_time:
                    logger.warning("hacker.last_time < cached.last_time")
                    hacker.last_name = cached.last_name
                    hacker.last_time = cached.last_time
                    hacker.s_last_time = cached.s_last_time

            self._hackers_by_steamid[hacker.steamid] = hacker

    def __str__(self):
        """Return database as `json` document."""

        jdoc = {
            "$schema": "https://raw.githubusercontent.com/PazerOP/tf2_bot_detector/master/schemas/v3/playerlist.schema.json",  # noqa
            "file_info": {
                "authors": ["pazer"],
                "description": "Official player blacklist for TF2 Bot Detector.",
                "title": "Official player blacklist",
                "update_url": "https://raw.githubusercontent.com/PazerOP/tf2_bot_detector/master/staging/cfg/playerlist.official.json",  # noqa
            },
            "players": [x.as_json for x in self._hackers_by_steamid.values()],
        }
        return json.dumps(jdoc, indent=4) + "\n"

    def save_database(self):
        """Write database to disk."""

        logger.info(f"Writing `--hackers` database at `{self._path}`")
        self._path.write_text(str(self), encoding="utf-8")

    def lookup_steamid(self, steamid) -> Hacker:
        """Return `Hacker` for given steamid, else None if not found."""

        logger.trace(f"steamid {steamid.id}")
        return self._hackers_by_steamid.get(steamid)

    def add(self, steamid, attributes, name) -> Hacker:
        """Create new `Hacker`, add to database, and return it."""

        now = int(time.time())
        hacker = Hacker(
            {
                "attributes": [HackerAttr(x) for x in attributes],
                "last_seen": {
                    "player_name": name,
                    "time": now,
                    "time_string": time.strftime(FMT_TIME, time.localtime(now)),
                },
                "steamid": steamid,
                "names": [name],
            }
        )
        self._hackers_by_steamid[hacker.steamid] = hacker
        return hacker

    def load_gamebots(self, path) -> None:
        """Read and create `GAMEBOT`s from list of names read from `path`.

        Used by qvalve; not used by tf2mon.
        """

        steamid = BOT_STEAMID

        with open(path, encoding="utf-8") as file:
            for (name,) in csv.reader(file):
                self.add(steamid, HackerAttr.GAMEBOT, name)

    def print_report(self) -> None:
        """Print database report."""

        table = TextTable(
            [
                TextColumn(-10, "STEAMID"),
                TextColumn(10, "ATTRS"),
                TextColumn(25, "LASTTIME"),
                TextColumn(30, "LASTNAME"),
                TextColumn(0, "NAMES"),
            ]
        )

        print(table.formatted_header)

        last_id = None  # check for duplicates

        for hacker in sorted(
            self._hackers_by_steamid.values(),
            key=lambda x: x.last_time,
            reverse=True,
        ):
            assert last_id != hacker.steamid.id
            last_id = hacker.steamid.id

            attributes = hacker.attributes.copy()
            attr = attributes.pop(0).value if len(attributes) > 0 else ""

            names = hacker.names.copy()
            name = names.pop(0).replace("\n", ".") if len(names) > 0 else ""

            print(
                table.format_detail(
                    hacker.steamid.id,
                    attr,
                    hacker.s_last_time or "",
                    hacker.last_name.replace("\n", ".") if hacker.last_name else "",
                    name.replace("\n", "."),
                )
            )

            while True:
                attr = attributes.pop(0).value if len(attributes) > 0 else ""
                name = names.pop(0).replace("\n", ".") if len(names) > 0 else ""
                if not attr and not name:
                    break
                print(table.format_detail(hacker.steamid.id, attr, "", "", name))
