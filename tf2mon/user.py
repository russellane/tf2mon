"""A user of the game."""

import re
from enum import Enum
from typing import NewType

from fuzzywuzzy import fuzz
from loguru import logger

from tf2mon.hacker import HackerAttr

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
    DELETE = "D"


class User:
    """A user of the game."""

    # pylint: disable=too-many-instance-attributes

    _milenko_re = re.compile(
        "|".join(
            [
                "I am a bot. I will leave in 15 seconds if there are no malicious"
                " bots to kick. https://milenko-tf2.github.io/",
                "No bots detected. GLHF! Anti-bot FAQ, Discord, and donations can"
                " be found at https://milenko-tf2.github.io/",
                "No bots detected. GLHF! https://incontestableness.github.io/milenko",
                "I am an anti-bot bot. I will leave in 15 seconds if there are no"
                " malicious bots to kick.",
                "Please press F2 to vote No, I leave automatically after about 15"
                " seconds if there are no malicious bots!",
                "No bots detected. Good luck, have fun!",
            ]
        )
    )

    def is_milenko_chat(self, chat):
        """Return True if this user appears to be milenko."""
        return self._milenko_re.search(chat.msg)

    _cheater_re = re.compile(
        "|".join(
            [
                "UNCLETOPIA.COM BEST MODERATED SERVERS! NO BOTS NO CHEATERS!",
            ]
        )
    )

    def is_cheater_chat(self, chat):
        """Return True first time chat appears to be from a cheater."""

        if self.cheater_chat_seen:
            return False
        self.cheater_chat_seen = self._cheater_re.search(chat.msg)
        return self.cheater_chat_seen

    def __init__(self, monitor, username):
        """Create `User`."""

        self.monitor = monitor
        self.username = username.replace(";", ".")

        if m := self.monitor._racist_re.search(self.username):
            self._clean_username = (
                m.string[: m.start()] + str("n" * (m.end() - m.start())) + m.string[m.end() :]
            )
        else:
            self._clean_username = self.username

        # too strict?
        if "\u0e31" in self.username:
            self.username = self.username.replace("\u0e31", "?")
            logger.warning(f"'\u0e31' in {self.username!r}")

        #
        self.username_upper = username.upper()
        self.userid = 0  # from status command
        self.steamid = None  # from status and tf_lobby_debug commands
        self.team = None
        self.ping = 0

        self.state = UserState.ACTIVE
        self.n_status_checks = 0
        self.nsnipes = 0
        self.role = self.monitor.unknown_role
        self.ncaptures = 0
        self.ndefenses = 0
        self.chats = []
        self.display_level = None
        self.selected = False
        self.perk = None

        #
        self.opponents: dict[User, User] = {}
        self.victims: dict[User, User] = {}
        self.killers: dict[User, User] = {}

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
        self.actions = []

        #
        self.hacker = None  # don't use unless vetted
        self.steamplayer = None  # don't use unless vetted
        self.vetted = False

        # When attempting to kick/track before hacker is available, this
        # indicates: a) the work (kick/track) has been postponed, and b)
        # the `HackerAttr.HackerAttr` to use when able to perform the work.

        self.work_attr = None

        # If this looks like a cheater we're tracking by name, mark him to
        # be kicked when his steamid becomes available. Doing this now to
        # notify the operator asap to `TF2MON-PUSH` steamids to us.
        # Careful, this might be a legitimate name-change, not a cheating name-stealer.

        self.cloner = None  # when this user is being cloned
        self.clonee = None  # when this user is the name-stealing clone

        if self._is_cheater_name(self.username):
            self.kick(HackerAttr.CHEATER)

        if self.monitor.is_racist_text(self.username):
            self.kick(HackerAttr.RACIST)

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

        if not self.monitor.ui.show_kd.value:
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

        # assign any unassigned opponents

        for opponent in self.opponents.values():
            if not opponent.team:
                opponent.assign_team(self.opposing_team)
            if not self.team:
                self.assign_team(opponent.opposing_team)

    def vet_player(self):
        """Examine user."""

        assert not self.vetted
        assert self.steamid

        self.steamplayer = self.monitor.steam_web_api.find_steamid(self.steamid)
        if self.steamplayer.is_legitimate_game_bot:
            self.steamplayer.personaname = self.username
            self.vetted = True
            self.work_attr = None
            return

        logger.debug(f"{self} SteamPlayer={self.steamplayer}")

        # has an existing user changed his name to this self.username?
        #  user := self._is_alias():
        #   vetted = "vetted" if user.vetted else "unvetted"
        #   logger.log("ALIAS", f"{self} steamid matches {vetted} {user}")
        #   # delete this alias from list
        #   self.state = UserState.DELETE
        #   # change name
        #   user.username = self.username
        #   user.username_upper = self.username.upper()
        #   # re-vet with new name
        #   user.vetted = False
        #   user.hacker = None
        #   user.vet_player()
        #   return

        # known hacker?
        self.hacker = self.monitor.hackers.lookup_steamid(self.steamid)
        if self.hacker:
            logger.log("hacker", self.hacker)
        else:
            logger.trace(f"{self} is not a known hacker")

        # should he be known?
        if self.work_attr and not self.hacker:
            # yes, work had been postponed until steamid now available
            self.hacker = self.monitor.hackers.add(self.steamid, self.work_attr, self.username)
            logger.log(self.work_attr.name, f"{self} created {self.hacker}")

        if self.hacker:
            # he's known
            self.hacker.track_appearance(self.username)
            self.monitor.hackers.save_database()

            self.display_level = self.hacker.attributes[0].name

            if self.hacker.is_banned:
                self.kick()
            elif self.hacker.is_suspect:
                logger.log(self.display_level, f"{self._clean_username!r} is here")

        # vet only once
        self.vetted = True
        self.work_attr = None

    def kick(self, attr=None):
        """Kick this user."""

        if self.userid in self.monitor.users.kicked_userids:
            logger.debug(f"already kicked userid {self.userid}")
            return

        if self._track(attr or HackerAttr.CHEATER):
            # work postponed until steamid becomes available
            return

        if self.hacker.is_milenko:
            # don't kick milenko
            msg = str(
                f"say {self.monitor.appname} Hello Milenko "
                f"{self.username!r} steamid {self.steamid!r}, thank you."
            )
            self.monitor.kicks.push(msg)
            return

        if self.hacker.is_suspect:
            # don't kick suspects
            logger.debug(f"not kicking suspect {self.username!r} steamid {self.steamid!r}")
            return

        # work

        msg = f"say {self.monitor.appname} ALERT: "
        if self.hacker.is_racist:
            msg += f"RACIST {self._clean_username!r}"
        elif self.clonee:
            msg += f"NAME-STEALER {self.username!r}"
        else:
            msg += f"CHEATER {self.username!r}"

        msg += " is here"
        cmd = f"CALLVOTE KICK {self.userid}"
        msg += f", {cmd}"

        self.monitor.kicks.push(msg)
        self.monitor.kicks.push(cmd)
        self.monitor.users.kicked_userids[self.userid] = True

    def _track(self, attr):

        self.display_level = attr.name

        if not self.steamid:
            if not self.work_attr:
                self.work_attr = attr
                logger.log(
                    self.display_level, f"{self} needs steamid, Press KP_DOWNARROW to PUSH"
                )
                self.monitor.ui.notify_operator = True
                self.monitor.ui.sound_alarm = True
            return True  # postpone work

        if not self.work_attr:
            # not postponed
            self.work_attr = attr
        # else un-postponed

        # work
        if self.hacker:
            if self.work_attr not in self.hacker.attributes:
                self.hacker.attributes.append(self.work_attr)
                logger.log(self.display_level, f"{self} added {self.work_attr} to {self.hacker}")
                self.monitor.hackers.save_database()
            else:
                logger.debug(f"{self} hacker {self.hacker} already {self.work_attr}")
        else:
            self.hacker = self.monitor.hackers.add(self.steamid, self.work_attr, self.username)
            logger.log(self.display_level, f"{self} created hacker {self.hacker}")
            self.monitor.hackers.save_database()

        # work performed
        self.work_attr = None
        return False

    _cheaters_re = re.compile(
        "|".join(
            [
                r"^(\(\d+\))?Sydney",
                r"Swonk Bot",
                r"spoooky braaaap",
                r"Bot Removal Service",
            ]
        )
    )

    def _is_cheater_name(self, name):

        if self._cheaters_re.search(name):
            return True

        for user in [x for x in self.monitor.users.active_users() if x.vetted and not x.hacker]:
            ratio = fuzz.ratio(name, user.username)
            if ratio > 80:
                logger.log("FUZZ", f"ratio {ratio} {name!r} vs {user.username!r}")
                # Careful, this might be a legitimate name-change, not a cheating name-stealer.
                user.cloner = self  # point the original user to the clone
                self.clonee = user  # point the clone to the original user
                return True

        return False

    def _is_alias(self):
        """Return the `User` that matches this user's steamid, else None."""

        users = [
            x
            for x in self.monitor.users.active_users()
            if x != self and x.steamid == self.steamid
        ]
        return users[0] if users else None
