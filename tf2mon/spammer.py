"""Spam generator."""

from loguru import logger

from tf2mon.toggle import Cycle


class Spammer:
    """Spam generator."""

    _insults = Cycle(
        "insults",
        [
            "noob",
            "try-hard",
            "wanker",
        ],
    )

    _killed = Cycle(
        "v",
        [
            "Killed",
            # "Murdered",
            # "Slaughtered",
            # "Butchered",
            # "Exterminated",
            # "Destroyed",
            # "Annihilated",
            # "Liquidated",
            # "Decimated",
            # "Done-in",
            # "Eliminated",
            # "Eviscerated",
            # "Massacred",
            # "Snuffed-out",
        ],
    )

    _crit_taunts = Cycle(
        "ct",
        [
            # "{killed} {user} with my {weapon} +crit; {duel}",
            "{duel} vs {user}, {weapon}, +crit",
        ],
    )

    _no_crit_taunts = Cycle(
        "nct",
        [
            # "{killed} {user} with my {weapon}; {duel}",
            "{duel} vs {user}, {weapon}",
        ],
    )

    _crit_throes = Cycle(
        "cg",
        [
            # "Nice crit with that {weapon}, {user}, you {insult}!",
            "{killed} by {user} with the {weapon} +crit",
            # "{duel} vs {user}, {weapon}, +crit",
        ],
    )

    _no_crit_throes = Cycle(
        "ncg",
        [
            # "Nice {weapon} ya got there, {user}, you {insult}!",
            "{killed} by {user} with the {weapon}",
            # "{duel} vs {user}, {weapon}",
        ],
    )

    _airblast_weapons = ("world", "deflect_promode", "deflect_rocket")

    def __init__(self, monitor):
        """Initialize."""
        self.monitor = monitor

    def taunt(self, victim, weapon, crit):
        """Make noise when operator kills opponent."""

        if self.monitor.ui.taunt_flag.value:
            self._push_spam(self._crit_taunts if crit else self._no_crit_taunts, victim, weapon)

    def throe(self, killer, weapon, crit):
        """Make noise when opponent kills operator."""

        if self.monitor.ui.throe_flag.value:
            spam = self._crit_throes if crit else self._no_crit_throes
            suffix = (" +" + killer.perk) if killer.perk else ""
            self._push_spam(spam, killer, weapon, suffix)

    def _is_airblast(self, weapon):

        return weapon in self._airblast_weapons

    def _push_spam(self, messages, user, weapon, suffix=""):

        m = messages.cycle.format(
            user=user.moniker,
            duel=self.monitor.my.duel_as_str(user),
            weapon=weapon,
            killed=self._killed.cycle,
            insult=self._insults.cycle,
        )
        self.monitor.spams.push("say " + m + suffix)

    def spam(self, spamno):
        """Respond to SPAM command."""

        if spamno == 1:
            msg = str(
                "say Real-time stats brought to you by " f"{self.monitor.appname} bot detector"
            )

        else:
            logger.critical(f"bad spamno {spamno!r}")
            return

        self.monitor.spams.pushleft(msg)
