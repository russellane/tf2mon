"""Gameplay patterns/handlers."""

from loguru import logger

from tf2mon.chat import Chat
from tf2mon.hacker import HackerAttr
from tf2mon.regex import Regex
from tf2mon.steamplayer import steamid_from_str
from tf2mon.user import Team, UserState


class Gameplay:
    """Gameplay."""

    # pylint: disable=line-too-long
    # pylint: disable=too-few-public-methods

    def __init__(self, monitor):
        """Initialize Gameplay."""

        self.monitor = monitor

        self.regex_list = [
            # key_listboundkeys
            # Regex(
            #    '^".*" = ".*"$',
            #    lambda m: logger.debug('key_listboundkeys')),
            # new server
            Regex(
                "(^Client reached server_spawn.$|^Connected to [0-9])",
                lambda m: self.monitor.reset_game(),
            ),
            # capture/defend
            Regex(
                r"^(?P<username>.*) (?P<action>(?:captured|defended)) (?P<capture_pt>.*) for team #(?P<teamno>\d)$",  # noqa
                lambda m: self._capture(
                    m.group("username"),
                    m.group("action"),
                    m.group("capture_pt"),
                    int(m.group("teamno")),
                ),
            ),
            # must be before `chat`
            # account : not logged in  (No account specified)
            # version : 6173888/24 6173888 secure
            # map     : pl_barnblitz at: 0 x, 0 y, 0 z
            # udp/ip  : 208.78.164.167:27067  (public ip: 208.78.164.167)
            # tags    : hidden,increased_maxplayers,payload,valve
            # steamid : [A:1:3814649857:15826] (90139968514486273)
            # players : 20 humans, 0 bots (32 max)
            # edicts  : 1378 used of 2048 max
            Regex(
                r"^(account|version|map|udp\/ip|tags|steamid|players|edicts)\s+: (.*)",
                lambda m: logger.log("server", m.group(0)),
            ),
            # chat
            # 'Bad Dad :  hello'
            # '*DEAD* Bad Dad :  hello'
            # '*DEAD*(TEAM) Bad Dad :  hello'
            Regex(
                r"^(?:(?P<dead>\*DEAD\*)?(?P<teamflag>\(TEAM\))? )?(?P<username>.*) :  ?(?P<msg>.*)$",  # noqa
                lambda m: self._playerchat(
                    m.group("teamflag"), m.group("username"), m.group("msg")
                ),
            ),
            # kill
            Regex(
                r"^(?P<killer>.*) killed (?P<victim>.*) with (?P<weapon>.*)\.(?P<crit> \(crit\))?$",  # noqa
                lambda m: self._kill(
                    m.group("killer"), m.group("victim"), m.group("weapon"), m.group("crit")
                ),
            ),
            # connected
            Regex(
                "^(?P<username>.*) connected$", lambda m: self._connected(m.group("username"))
            ),
            # status
            # "# userid name                uniqueid            connected ping loss state"
            # "#     29 "Bad Dad"           [U:1:42708103]      01:24       67    0 active"
            Regex(
                r'^#\s*(?P<userid>\d+) "(?P<username>.+)"\s+(?P<steamid>\S+)\s+(?P<elapsed>[\d:]+)\s+(?P<ping>\d+)',  # noqa
                lambda m: self._status(
                    int(m.group("userid")),
                    m.group("username"),
                    m.group("steamid"),
                    m.group("ping"),
                ),
            ),
            # status
            # "# userid name                uniqueid            connected ping loss state"
            # "#      3 "Nobody"            BOT                                     active
            Regex(
                r'^#\s*(?P<userid>\d+) "(?P<username>.+)"\s+(?P<steamid>BOT)\s+active',
                lambda m: self._status(
                    int(m.group("userid")),
                    m.group("username"),
                    m.group("steamid"),
                    0,
                ),
            ),
            # tf_lobby_debug
            # "Member[22] [U:1:42708103]  team = TF_GC_TEAM_INVADERS  type = MATCH_PLAYER"
            Regex(
                r"^\s*(Member|Pending)\[\d+\] (?P<steamid>\S+)\s+team = (?P<teamname>\w+)",
                lambda m: self._lobby(m.group("steamid"), m.group("teamname")),
            ),
            Regex(
                "^Failed to find lobby shared object",
                lambda m: logger.trace("tf_lobby_debug failed: " + m.group(0)),
            ),
            #
            # Regex(
            #    '^Teams have been switched',
            #    lambda m: self.monitor.switch_teams()),
            #
            Regex(
                r"^You have switched to team (?P<teamname>\w+) and will",
                lambda m: self.monitor.me.assign_team(m.group("teamname")),
            ),
            # hostname: Valve Matchmaking Server (Virginia iad-1/srcds148 #53)
            Regex(
                "^hostname: (.*)",
                lambda m: (
                    logger.log("server", m.group(0)),
                    self.monitor.users.check_status(),
                ),
            ),
            # "FFD700[RTD] FF4040your mother rolled 32CD32PowerPlay."
            Regex(
                r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*) rolled [0-9A-F]{6}(?P<perk>.*)",  # noqa
                lambda m: self._perk(m.group("username"), m.group("perk")),
            ),
            Regex(
                r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*)\'s perk has worn off.",
                lambda m: self._perk(m.group("username"), None),
            ),
            Regex(
                r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*) has changed class during their roll.",  # noqa
                lambda m: self._perk(m.group("username"), None),
            ),
            Regex(
                r"[0-9A-F]{6}\[RTD\] Your perk has worn off.", lambda m: self._perk(None, None)
            ),
        ]

    def _capture(self, username, action, capture_pt, teamno):

        for name in username.split(", "):  # fix: names containing commas

            user = self.monitor.users.find_username(name)

            user.assign_teamno(teamno)

            if action == "captured":
                user.ncaptures += 1
                level = "CAP"
            else:
                user.ndefenses += 1
                level = "DEF"
            level += user.team.name

            logger.log(level, f"{user} {capture_pt!r}")
            user.actions.append(f"{level} {capture_pt!r}")

    def _playerchat(self, teamflag, username, msg):

        user = self.monitor.users.find_username(username)
        chat = Chat(user, teamflag, msg)

        user.chats.append(chat)
        self.monitor.ui.show_chat(chat)

        # if this is a team chat, then we know we're on the same team, and
        # if one of us knows which team we're on and the other doesn't, we
        # can assign.

        me = my = self.monitor.me
        if chat.teamflag and user != me:
            # we're on the same team
            if not user.team:
                if my.team:
                    user.assign_team(my.team)
            elif not my.team:
                me.assign_team(user.team)

        # inspect msg
        if self.monitor.is_racist_text(chat.msg):
            user.kick(HackerAttr.RACIST)

        # If this looks like a milenko chat, mark him to be tracked when
        # his steamid becomes available. Doing this now to notify the
        # operator asap to `TF2MON-PUSH` steamids to us.
        #
        # Why track them? No requirement; curious to see relationship
        # between names and steamids... one-to-one, many-to-one?

        elif user.is_milenko_chat(chat):
            user.kick(HackerAttr.MILENKO)

        elif user.is_cheater_chat(chat):
            user.kick(HackerAttr.CHEATER)

    def _kill(self, s_killer: str, s_victim: str, weapon: str, s_crit: str) -> None:

        killer = self.monitor.users.find_username(s_killer)
        victim = self.monitor.users.find_username(s_victim)

        killer.last_victim = victim
        victim.last_killer = killer

        # do most calculations now (once);
        # to avoid calculating when rendering scoreboard (often).

        killer.opponents[victim] = victim
        victim.opponents[killer] = killer

        killer.victims[victim] = victim
        victim.killers[killer] = killer

        # totals ---------------------------------------------------------------

        killer.nkills += 1
        victim.ndeaths += 1

        _k = killer.nkills
        _d = killer.ndeaths
        killer.kdratio = _k if not _d else _k / _d

        _k = victim.nkills
        _d = victim.ndeaths
        victim.kdratio = _k if not _d else _k / _d

        # subtotals by opponent-------------------------------------------------

        killer.nkills_by_opponent[victim] += 1
        victim.ndeaths_by_opponent[killer] += 1

        _k = killer.nkills_by_opponent[victim]
        _d = killer.ndeaths_by_opponent[victim]
        killer.kdratio_by_opponent[victim] = _k if not _d else _k / _d

        _k = victim.nkills_by_opponent[killer]
        _d = victim.ndeaths_by_opponent[killer]
        victim.kdratio_by_opponent[killer] = _k if not _d else _k / _d

        # subtotal opponents by weapon_state -----------------------------------

        if role := self.monitor.role_by_weapon.get(weapon):
            killer.role = role
            if killer.role == self.monitor.sniper_role:
                killer.nsnipes += 1
        else:
            role = killer.role
            if weapon not in ("player", "world"):
                logger.error(f"cannot map {weapon} for {killer}")

        crit = bool(s_crit)
        weapon_state = role.get_weapon_state(weapon, crit, killer.perk)

        killer.nkills_by_opponent_by_weapon[victim][weapon_state] += 1
        victim.ndeaths_by_opponent_by_weapon[killer][weapon_state] += 1

        #
        level = "KILL"
        if killer.team:
            level += killer.team.name

        logger.log(level, weapon_state)

        if killer == self.monitor.me:
            self.monitor.spammer.taunt(victim, weapon, crit)

        if victim == self.monitor.me:
            self.monitor.spammer.gurgle(killer, weapon, crit)

        if not victim.team and killer.team:
            victim.assign_team(killer.opposing_team)
        elif not killer.team and victim.team:
            killer.assign_team(victim.opposing_team)

    def _connected(self, username):

        logger.log("CONNECT", self.monitor.users.find_username(username))

        self.monitor.ui.notify_operator = True

    def _status(self, userid, username, s_steamid, ping):

        self.monitor.ui.notify_operator = False
        if not (steamid := steamid_from_str(s_steamid)):
            return  # invalid

        self.monitor.users.status(userid, username, steamid, ping)

    def _lobby(self, s_steamid, teamname):

        # this will not be called for games on local server with bots
        # or community servers; only on valve matchmaking servers.

        if not (steamid := steamid_from_str(s_steamid)):
            return  # invalid

        if teamname == "TF_GC_TEAM_INVADERS":
            team = Team.BLU
        elif teamname == "TF_GC_TEAM_DEFENDERS":
            team = Team.RED
        else:
            logger.critical(f"bad teamname {teamname!r} steamid {steamid}")
            return

        self.monitor.users.lobby(steamid, team)

    def _perk(self, username, perk):

        user = self.monitor.users.find_username(username) if username else self.monitor.me

        if perk:
            logger.log("PERK-ON", f"{user} {perk!r}")
        else:
            logger.log("PERK-OFF", f"{user} {user.perk!r}")

        user.perk = perk

    def repl(self):
        """Read the console log file and play game."""

        self.monitor.steam_web_api.connect()
        self.monitor.conlog.open()

        #
        while (line := self.monitor.conlog.readline()) is not None:

            if not line:  # blank line
                continue

            regex = Regex.search_list(line, self.monitor.regex_list)
            if not regex:
                logger.log("ignore", self.monitor.conlog.last_line)
                continue

            self.monitor.admin.check_single_step(line)

            regex.handler(regex.re_match_obj)

            # Vet all unvetted users that can be vetted, and perform all
            # postponed work that can be performed.

            for user in self.monitor.users.active_users():

                if not user.vetted and user.steamid:
                    user.vet_player()

                if user.vetted and user.work_attr:
                    user.kick()

                if user.state == UserState.DELETE:
                    self.monitor.users.delete(user)

            # push work to the game
            self.monitor.msgqueues.send()

            #
            self.monitor.ui.update_display()
