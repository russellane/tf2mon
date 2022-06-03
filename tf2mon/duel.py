"""Duel.

A contest with deadly weapons arranged between two people in order to
settle a point of honor.
"""

from dataclasses import InitVar, dataclass

from tf2mon.user import User


@dataclass
class Duel:
    """A contest between players."""

    killer: User
    victim: User
    weapon: InitVar[str]
    crit: InitVar[bool]
    key: str = None

    def __post_init__(self, weapon, crit) -> None:
        """Create hashable key for this unique "weapon-state".

        Also used as the formatted display value (for this unique "weapon-state").
        """

        name = self.killer.role.name if self.killer.role else ""
        crit = "+crit" if crit else ""
        perk = "+" + self.killer.perk if self.killer.perk else ""

        self.key = " ".join(
            [
                f"{name:8}",  # 8=len("engineer")
                f"{crit:5}",  # 5=len("+crit")
                f"{weapon:26}",  # 26=len("tf_projectile_pipe_remote")
                perk,
            ]
        ).rstrip()
