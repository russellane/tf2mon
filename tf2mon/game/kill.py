import re

from loguru import logger

import tf2mon
from tf2mon.game import GameEvent
from tf2mon.role import Role, get_role_weapon_state
from tf2mon.spammer import Spammer
from tf2mon.users import Users


class GameKillEvent(GameEvent):

    pattern = r"(?P<killer>.*) killed (?P<victim>.*) with (?P<weapon>.*)\.(?P<crit> \(crit\))?$"
    spammer = Spammer()

    def handler(self, match: re.Match) -> None:

        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements

        s_killer, s_victim, weapon, s_crit = match.groups()

        killer = Users[s_killer]
        victim = Users[s_victim]

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

        crit = bool(s_crit)
        role, weapon_state = get_role_weapon_state(killer.role, weapon, crit, killer.perk)
        if role:
            killer.role = role
            if killer.role == Role.sniper:
                killer.nsnipes += 1
        else:
            role = killer.role
            if weapon not in ("player", "world"):
                logger.error(f"cannot map {weapon} for {killer} {role}")

        if not role and weapon not in ("player", "world"):
            logger.error(f"cannot map {weapon} for {killer} {role}")

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

        if tf2mon.ShowKillsControl.value:
            level = "KILL"
            if killer.team:
                level += killer.team.name
            tf2mon.ui.show_journal(
                level,
                f"         {killer.moniker!r:25} killed {victim.moniker!r:25} {weapon_state!r}",
            )

        if killer == Users.me:
            if tf2mon.TauntFlagControl.value:
                self.spammer.taunt(victim, weapon, crit)
        elif victim == Users.me and tf2mon.ThroeFlagControl.value:
            self.spammer.throe(killer, weapon, crit)

        if not victim.team and killer.team:
            victim.assign_team(killer.opposing_team)
        elif not killer.team and victim.team:
            killer.assign_team(victim.opposing_team)
