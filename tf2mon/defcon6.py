"""Defcon6 attributes."""

from collections import defaultdict

from sqlalchemy import select

from tf2mon.player import Player


def get_defcon6(session) -> dict[int, list[str]]:
    """Return defcon6 attributes."""

    attrs = defaultdict(list)  # k=steamid, v=list[attrs]

    stmt = select(Player)
    for player in session.scalars(stmt):
        if player.bot:
            attrs[player.steamid].append(player.bot)
        if player.friends:
            attrs[player.steamid].append(player.friends)
        if player.tacobot:
            attrs[player.steamid].append(player.tacobot)
        if player.pazer:
            attrs[player.steamid].append(player.pazer)

    return attrs


if __name__ == "__main__":
    from pprint import pprint

    from tf2mon.database import Session  # noqa

    _session = Session(".cache/tf2mon.db")
    _attrs = get_defcon6(_session)
    _session.close()
    pprint(_attrs)
