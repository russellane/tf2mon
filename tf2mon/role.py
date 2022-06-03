"""Role (job, function, position) of `User`."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Role:
    """Role (job, function, position) of `User`."""

    name: str  # match tokens in `con_logfile` and `weapons.csv`
    display: str  # for scoreboard

    @staticmethod
    def get_roles_by_name() -> Dict:
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
        ]:
            roles[name] = Role(name, display)

        return roles
