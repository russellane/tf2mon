"""Role (job, function, position) of `User`."""

import csv
from enum import Enum
from pathlib import Path
from typing import Tuple

from loguru import logger

Role = Enum("Role", "scout soldier pyro demo heavy engineer medic sniper spy unknown")

_ROLE_BY_WEAPON: dict[str, Role] = {}


def load_weapons_data(path: Path) -> None:
    """Load weapons data from `path`."""

    global _ROLE_BY_WEAPON  # pylint: disable=global-statement

    logger.info(f"Reading `{path}`")
    with open(path, encoding="utf-8") as _f:
        _ROLE_BY_WEAPON = {
            weapon: Role.__dict__[role_name] for role_name, weapon in csv.reader(_f)
        }


def get_role_weapon_state(
    default_role: Role, weapon: str, crit: bool, perk: str
) -> Tuple[Role, str]:
    """Return role and hashable key for given weapon_state.

    Also used as the formatted display value by scoreboard.
    """

    role = _ROLE_BY_WEAPON.get(weapon, default_role)

    s_crit = "+crit" if crit else ""
    s_perk = "+" + perk if perk else ""

    weapon_state = " ".join(
        [
            f"{role.name:8}",  # 8=len("engineer")
            f"{s_crit:5}",  # 5=len("+crit")
            f"{weapon:26}",  # 26=len("tf_projectile_pipe_remote")
            s_perk,  # 20=len("Infinite Double Jump")
        ]
    ).rstrip()

    return role, weapon_state
