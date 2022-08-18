"""Gameplay patterns/handlers."""

from loguru import logger

import tf2mon
from tf2mon.chat import Chat
from tf2mon.player import Player
from tf2mon.regex import Regex


class Gameplay:
    """Gameplay."""

    # pylint: disable=line-too-long

    def __init__(self):
        """Initialize Gameplay."""

        leader = (
            r"^(\d{2}/\d{2}/\d{4} - \d{2}:\d{2}:\d{2}: )?"  # anchor to head; optional timestamp
        )

        self.regex_list = [
            # new server
            Regex(
                leader + "(Client reached server_spawn.$|Connected to [0-9])",
                lambda m: tf2mon.monitor.reset_game(),
            ),
            # capture/defend
            Regex(
                leader
                + r"(?P<username>.*) (?P<action>(?:captured|defended)) (?P<capture_pt>.*) for team #(?P<s_teamno>\d)$",  # noqa
                lambda m: self.capture(*m.groups()),
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
                leader + r"(account|version|map|udp\/ip|tags|steamid|players|edicts)\s+: (.*)",
                lambda m: ...,  # logger.log("server", m.group(0)),
            ),
            # "06/05/2022 - 13:54:19: Client ping times:"
            Regex(
                leader + r"Client ping times:",
                lambda m: ...,  # logger.log("server", m.group(0)),
            ),
            # "06/05/2022 - 13:54:19:   67 ms : luft"
            # "06/05/2022 - 13:54:19:xy 87 ms : BananaHatTaco"
            Regex(
                leader + r"\s*\d+ ms .*",
                lambda m: ...,  # logger.log("server", m.group(0)),
            ),
            # chat
            # 'Bob :  hello'
            # '*DEAD* Bob :  hello'
            # '*DEAD*(TEAM) Bob :  hello'
            Regex(
                leader
                + r"(?:(?P<dead>\*DEAD\*)?(?P<teamflag>\(TEAM\))? )?(?P<username>.*) :  ?(?P<msg>.*)$",  # noqa
                lambda m: self.playerchat(*m.groups()),
            ),
            # kill
            Regex(
                leader
                + r"(?P<killer>.*) killed (?P<victim>.*) with (?P<weapon>.*)\.(?P<crit> \(crit\))?$",  # noqa
                lambda m: self.kill(*m.groups()),
            ),
            # connected
            Regex(
                leader + "(?P<username>.*) connected$",
                lambda m: self.connected(*m.groups()),
            ),
            # status
            # "# userid name                uniqueid            connected ping loss state"
            # "#     29 "Bob"               [U:1:99999999]      01:24       67    0 active"
            # "#    158 "Jones"             [U:1:9999999999]     2:21:27    78    0 active
            Regex(
                leader
                + r'#\s*(?P<s_userid>\d+) "(?P<username>.+)"\s+(?P<steamid>\S+)\s+(?P<elapsed>[\d:]+)\s+(?P<ping>\d+)',  # noqa
                lambda m: self.status(*m.groups()),
            ),
            # status
            # "# userid name                uniqueid            connected ping loss state"
            # "#      3 "Nobody"            BOT                                     active
            Regex(
                leader + r'#\s*(?P<userid>\d+) "(?P<username>.+)"\s+(?P<steamid>BOT)\s+active',
                lambda m: self.status(*m.groups(), "", 0),
            ),
            # tf_lobby_debug
            # "Member[22] [U:1:99999999]  team = TF_GC_TEAM_INVADERS  type = MATCH_PLAYER"
            Regex(
                leader
                + r"\s*(?:Member|Pending)\[\d+\] (?P<steamid>\S+)\s+team = (?P<teamname>\w+)",
                lambda m: self.lobby(*m.groups()),
            ),
            Regex(
                leader + "Failed to find lobby shared object",
                lambda m: logger.trace("tf_lobby_debug failed: " + m.group(0)),
            ),
            #
            # Regex(
            #    '^Teams have been switched',
            #    lambda m: tf2mon.monitor.switch_teams()),
            #
            Regex(
                leader + r"You have switched to team (?P<teamname>\w+) and will",
                lambda m: tf2mon.monitor.me.assign_team(m.group("teamname")),
            ),
            # hostname: Valve Matchmaking Server (Virginia iad-1/srcds148 #53)
            Regex(
                "^hostname: (.*)",
                lambda m: tf2mon.monitor.users.check_status(),
            ),
            # "FFD700[RTD] FF4040your mother rolled 32CD32PowerPlay."
            Regex(
                r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*) rolled [0-9A-F]{6}(?P<perk>.*)",  # noqa
                lambda m: self.perk(*m.groups()),
            ),
            Regex(
                r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*)\'s perk has worn off.",
                lambda m: self.perk(*m.groups(), None),
            ),
            Regex(
                r"[0-9A-F]{6}\[RTD\] [0-9A-F]{6}(?P<username>.*) has changed class during their roll.",  # noqa
                lambda m: self.perk(*m.groups(), None),
            ),
            Regex(
                r"[0-9A-F]{6}\[RTD\] Your perk has worn off.", lambda m: self.perk(None, None)
            ),
        ]

    def capture(self, _leader, username, action, capture_pt, s_teamno):
        """Handle message."""

        for name in username.split(", "):  # fix: names containing commas

            user = tf2mon.monitor.users.find_username(name)

            user.assign_teamno(int(s_teamno))

            if action == "captured":
                user.ncaptures += 1
                level = "CAP"
            else:
                user.ndefenses += 1
                level = "DEF"
            user.dirty = True
            level += user.team.name

            logger.log(level, f"{user} {capture_pt!r}")
            user.actions.append(f"{level} {capture_pt!r}")

    def playerchat(self, _leader, _dead, teamflag, username, msg):
        """Handle message."""

        user = tf2mon.monitor.users.find_username(username)
        chat = Chat(user, teamflag, msg)

        user.chats.append(chat)
        tf2mon.monitor.chats.append(chat)
        tf2mon.monitor.ui.show_chat(chat)

        # if this is a team chat, then we know we're on the same team, and
        # if one of us knows which team we're on and the other doesn't, we
        # can assign.

        me = my = tf2mon.monitor.me
        if chat.teamflag and user != me:
            # we're on the same team
            if not user.team:
                if my.team:
                    user.assign_team(my.team)
            elif not my.team:
                me.assign_team(user.team)

        # inspect msg
        if tf2mon.monitor.is_racist_text(chat.msg):
            user.kick(Player.RACIST)

        elif user.is_cheater_chat(chat):
            user.kick(Player.CHEATER)

    def kill(self, _leader, s_killer: str, s_victim: str, weapon: str, s_crit: str) -> None:
        """Handle message."""

        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements

        killer = tf2mon.monitor.users.find_username(s_killer)
        victim = tf2mon.monitor.users.find_username(s_victim)

        killer.last_victim = victim
        victim.last_killer = killer

        # do most calculations now (once);
        # to avoid calculating when rendering scoreboard (often).

        killer.opponents[victim.key] = victim
        victim.opponents[killer.key] = killer

        killer.victims[victim.key] = victim
        victim.killers[killer.key] = killer

        # totals ---------------------------------------------------------------

        killer.nkills += 1
        victim.ndeaths += 1
        killer.dirty = True
        victim.dirty = True

        _k = killer.nkills
        _d = killer.ndeaths
        killer.kdratio = float(_k) if not _d else _k / _d

        _k = victim.nkills
        _d = victim.ndeaths
        victim.kdratio = float(_k) if not _d else _k / _d

        # subtotals by opponent-------------------------------------------------

        if victim.key not in killer.nkills_by_opponent:
            killer.nkills_by_opponent[victim.key] = 0
        killer.nkills_by_opponent[victim.key] += 1

        if killer.key not in victim.ndeaths_by_opponent:
            victim.ndeaths_by_opponent[killer.key] = 0
        victim.ndeaths_by_opponent[killer.key] += 1

        _k = killer.nkills_by_opponent.get(victim.key, 0)
        _d = killer.ndeaths_by_opponent.get(victim.key, 0)
        killer.kdratio_by_opponent[victim.key] = float(_k) if not _d else _k / _d

        _k = victim.nkills_by_opponent.get(killer.key, 0)
        _d = victim.ndeaths_by_opponent.get(killer.key, 0)
        victim.kdratio_by_opponent[killer.key] = float(_k) if not _d else _k / _d

        # subtotal opponents by weapon_state -----------------------------------

        if role := tf2mon.monitor.role_by_weapon.get(weapon):
            killer.role = role
            if killer.role == tf2mon.monitor.sniper_role:
                killer.nsnipes += 1
        else:
            role = killer.role
            if weapon not in ("player", "world"):
                logger.error(f"cannot map {weapon} for {killer} {role}")

        crit = bool(s_crit)
        weapon_state = role.get_weapon_state(weapon, crit, killer.perk)

        if victim.key not in killer.nkills_by_opponent_by_weapon:
            # contains a hash of counts by weapon_state
            killer.nkills_by_opponent_by_weapon[victim.key] = {}
        if weapon_state not in killer.nkills_by_opponent_by_weapon[victim.key]:
            killer.nkills_by_opponent_by_weapon[victim.key][weapon_state] = 0
        killer.nkills_by_opponent_by_weapon[victim.key][weapon_state] += 1

        #
        level = "KILL"
        if killer.team:
            level += killer.team.name

        logger.log(
            level,
            "killer {!r} victim {!r} weapon {!r}",
            killer.moniker,
            victim.moniker,
            weapon_state,
        )

        if tf2mon.monitor.controls["ShowKillsControl"].value:
            level = "KILL"
            if killer.team:
                level += killer.team.name
            tf2mon.monitor.ui.show_journal(
                level,
                f"         {killer.moniker!r:25} killed {victim.moniker!r:25} {weapon_state!r}",
            )

        if killer == tf2mon.monitor.me:
            tf2mon.monitor.spammer.taunt(victim, weapon, crit)

        if victim == tf2mon.monitor.me:
            tf2mon.monitor.spammer.throe(killer, weapon, crit)

        if not victim.team and killer.team:
            victim.assign_team(killer.opposing_team)
        elif not killer.team and victim.team:
            killer.assign_team(victim.opposing_team)

    def connected(self, _leader, username):
        """Handle message."""

        logger.log("CONNECT", tf2mon.monitor.users.find_username(username))

        tf2mon.monitor.ui.notify_operator = True

    def status(self, _leader, userid, username, steamid, elapsed, ping):
        """Handle message."""

        # pylint: disable=too-many-arguments

        tf2mon.monitor.users.status(userid, username, steamid, elapsed, ping)

    def lobby(self, _leader, steamid, teamname):
        """Handle message."""

        tf2mon.monitor.users.lobby(steamid, teamname)

    def perk(self, username, perk):
        """Handle message."""

        user = tf2mon.monitor.users.find_username(username) if username else tf2mon.monitor.me

        if perk:
            logger.log("PERK-ON", f"{user} {perk!r}")
        else:
            logger.log("PERK-OFF", f"{user} {user.perk!r}")

        user.perk = perk
        user.dirty = True
