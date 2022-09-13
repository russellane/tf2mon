"""A user of the game."""

import re
from enum import Enum
from typing import List, NewType

from loguru import logger

import tf2mon
from tf2mon.chat import Chat
from tf2mon.player import Player
from tf2mon.racist import clean_username
from tf2mon.role import Role
from tf2mon.steamplayer import SteamPlayer

UserKey = NewType("UserKey", str)
WeaponState = NewType("WeaponState", str)


class Team(Enum):
    """Valid teams."""

    RED = 2
    BLU = 3


class UserState(Enum):
    """Valid states."""

    ACTIVE = "A"
    INACTIVE = "I"


class User:
    """A user of the game."""

    # pylint: disable=too-many-instance-attributes

    _re_cheater_chats = re.compile(
        "|".join(
            [
                "UNCLETOPIA.COM BEST MODERATED SERVERS! NO BOTS NO CHEATERS!",
                "m4gic m4gic",
            ]
        )
    )

    def is_cheater_chat(self, chat):
        """Return True first time chat appears to be from a cheater."""

        if self.cheater_chat_seen:
            return False
        self.cheater_chat_seen = self._re_cheater_chats.search(chat.msg)
        return self.cheater_chat_seen

    def __init__(self, username: str):
        """Create `User`."""

        self.username = username.replace(";", ".")
        self._clean_username = clean_username(self.username)

        # too strict?
        if "\u0e31" in self.username:
            # self.username = self.username.replace("\u0e31", "?")
            logger.warning(f"'\u0e31' in {self.username!r}")

        #
        self.username_upper = username.upper()
        self.userid = 0  # from status command
        self.steamid = None  # from status and tf_lobby_debug commands
        self.team = None
        self.elapsed: int = 0
        self.s_elapsed: str = ""
        self.ping = 0
        self.last_scoreboard_line = True
        self.dirty = True

        self.state = UserState.ACTIVE
        self.n_status_checks = 0
        self.nsnipes = 0
        self.role = Role.unknown
        self.ncaptures = 0
        self.ndefenses = 0
        self.chats: List[Chat] = []
        self.display_level = None
        self.selected = False
        self.perk = None

        #
        self.opponents: dict[UserKey, User] = {}
        self.victims: dict[UserKey, User] = {}
        self.killers: dict[UserKey, User] = {}

        self.last_killer: User = None
        self.last_victim: User = None

        self.nkills = 0
        self.ndeaths = 0
        self.kdratio: float = 0

        # "by" as in "lookup by", "for each", "per".
        self.nkills_by_opponent: dict[UserKey, int] = {}
        self.ndeaths_by_opponent: dict[UserKey, int] = {}
        self.kdratio_by_opponent: dict[UserKey, float] = {}
        self.nkills_by_opponent_by_weapon: dict[UserKey, dict[WeaponState, int]] = {}

        # list of non-kill actions performed, like capture/defend.
        self.actions: List[str] = []

        #
        self.steamplayer: SteamPlayer = None
        self.age = 0
        self.player: Player = None

        # Database `Player`s are keyed by `steamid`. If `self.kick(attr)`
        # is called before steamid is available, spool the work until it is.

        self.pending_attrs: list[str] = []

        # If this looks like a cheater we're tracking by name, mark him to
        # be kicked when his steamid becomes available. Doing this now to
        # notify the operator asap to `TF2MON-PUSH` steamids to us.
        # Careful, this might be a legitimate name-change, not a cheating name-stealer.

        self.cloner: User = None  # when this user is being cloned
        self.clonee: User = None  # when this user is the name-stealing clone

        self.cheater_chat_seen = False

    @property
    def key(self) -> str:
        """Return readable hashable key."""

        return f"{self.userid}-{self._clean_username[:15]}"

    @property
    def points(self):
        """Return number of points scored."""

        return self.nkills + self.ncaptures + self.ndefenses

    @property
    def opposing_team(self):
        """Return opposing team."""

        return Team.RED if self.team == Team.BLU else Team.BLU

    @property
    def moniker(self):
        """Return name, optionally including his kill/death ratio."""

        if not tf2mon.ShowKDControl.value:
            return self._clean_username

        # pylint: disable=consider-using-f-string

        if self.ndeaths < 2:
            return "{!r} ({}/{})".format(self._clean_username, self.nkills, self.ndeaths)

        return "{!r} ({}/{}={:.1f})".format(
            self._clean_username, self.nkills, self.ndeaths, self.nkills / self.ndeaths
        )

    def duel_as_str(self, opponent, formatted=False):
        """Return string showing win/loss record against `opponent`."""

        nkills = self.nkills_by_opponent.get(opponent.key, 0)
        ndeaths = self.ndeaths_by_opponent.get(opponent.key, 0)
        return f"{nkills:2} and {ndeaths:2}" if formatted else f"{nkills} and {ndeaths}"

    def __repr__(self):

        team = f"{self.team.name}:" if self.team else ""
        return f"{team}{self.userid}={self.username!r}"

    def assign_teamno(self, teamno):
        """Assign this user to `teamno`."""

        try:
            team = Team(teamno)
        except ValueError as err:
            logger.error(f"{err} teamno {teamno!r}")

        self.assign_team(team)

    def assign_team(self, team):
        """Assign this user to `team`."""

        if isinstance(team, str):
            if team == Team.RED.name:
                team = Team.RED
            elif team == Team.BLU.name:
                team = Team.BLU
            else:
                logger.critical(f"bad team {team!r}")
                return

        if not self.team:
            logger.info(f"{self} joins {team}")

        elif self.team != team:
            logger.debug(f"{self} change from {self.team} to {team}")

        self.team = team
        self.dirty = True

        # assign any unassigned opponents

        for opponent in self.opponents.values():
            if not opponent.team:
                opponent.assign_team(self.opposing_team)
            if not self.team:
                self.assign_team(opponent.opposing_team)

    def vet(self) -> None:
        """Vet this player, whose `steamid` has just been obtained."""

        assert self.steamid
        self.dirty = True

        self.steamplayer = tf2mon.steam_web_api.fetch_steamid(self.steamid.id)
        if self.steamplayer.is_gamebot:
            self.steamplayer.personaname = self.username
            self.pending_attrs = []
            return

        logger.log("SteamPlayer", f"{self} SteamPlayer={self.steamplayer}")
        self.age = self.steamplayer.age

        # known hacker?
        self.player = Player.fetch_steamid(self.steamid.id)
        if self.player:
            # logger.log("Player", self.player.astuple())
            self.player.setattrs(self.pending_attrs)
            self.player.track_appearance(self.username)
            tf2mon.ui.show_player_intel(self.player)
            # bobo1
            self.display_level = self.player.display_level
            # logger.log(self.display_level, f"{self._clean_username!r} is here")
            # bobo2
            self.pending_attrs = None
            if self.player.is_banned:
                self.do_kick()
            return
        logger.trace(f"{self} is not a known hacker")

        # Have we tried to kick them, but had to spool the work because
        # `steamid` wasn't available yet?
        if self.pending_attrs:
            self.player = Player.new_player(self.steamid.id, self.pending_attrs, self.username)
            # bobo1
            self.display_level = self.player.display_level
            logger.log(self.display_level, f"{self} created {self.player}")
            # bobo2
            self.pending_attrs = None
            if self.player.is_banned:
                self.do_kick()

    def kick(self, attr):
        """Kick this user."""

        if not self.steamid:
            # postpone work until steamid available
            self.pending_attrs.append(attr)
            self.display_level = attr.upper()
            logger.log(self.display_level, f"{self} needs steamid, Press KP_DOWNARROW to PUSH")
            tf2mon.notify_operator = True
            tf2mon.sound_alarm = True
            return

        if self.player:
            if not getattr(self.player, attr):
                self.player.setattrs([attr])
                self.player.upsert()
                logger.log(self.display_level, f"{self} added {attr} to {self.player}")
            else:
                logger.info(f"{self} player {self.player} already {attr}")
        else:
            self.player = Player.new_player(
                self.steamid.id, [attr] + self.pending_attrs, self.username
            )
            self.display_level = self.player.display_level
            logger.log(self.display_level, f"{self} created {self.player}")
            self.pending_attrs = None

        if self.player.is_banned:
            self.do_kick()

    def do_kick(self) -> None:
        """Work."""

        # msg = f"say {tf2mon.APPNAME} ALERT: "
        msg = "say ALERT: "
        if self.player.racist or self.player._racist:  # noqa
            msg += f"RACIST {self._clean_username!r}"
        elif self.clonee:
            msg += f"NAME-STEALER {self.username!r}"
        else:
            msg += f"CHEATER {self.username!r}"

        msg += " is here"
        cmd = f"CALLVOTE KICK {self.userid}"
        msg += f", {cmd}"

        tf2mon.KicksControl.push(msg)
        tf2mon.KicksControl.push(cmd)
