"""Role (job, function, position) of `User`."""

from dataclasses import dataclass


@dataclass
class Role:
    """Role (job, function, position) of `User`."""

    name: str  # match tokens in `con_logfile` and `weapons.csv`
    display: str  # for scoreboard

    @staticmethod
    def get_roles_by_name() -> dict:
        """Return `dict` of `Role`s indexed by name."""

        roles = {}
        for display, name in [
            ("C", "scout"),
            ("S", "soldier"),
            ("P", "pyro"),
            ("D", "demo"),
            ("E", "engineer"),
            ("H", "heavy"),
            ("M", "medic"),
            ("N", "sniper"),
            ("Y", "spy"),
            ("?", "unknown"),
        ]:
            roles[name] = Role(name, display)

        return roles

    def get_weapon_state(self, weapon: str, crit: bool, perk: str) -> str:
        """Return hashable key for given weapon_state.

        Also used as the formatted display value by scoreboard.
        """

        crit = "+crit" if crit else ""
        perk = "+" + perk if perk else ""

        return " ".join(
            [
                f"{self.name:8}",  # 8=len("engineer")
                f"{crit:5}",  # 5=len("+crit")
                f"{weapon:26}",  # 26=len("tf_projectile_pipe_remote")
                perk,
            ]
        ).rstrip()
