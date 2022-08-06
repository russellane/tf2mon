import pytest

from tf2mon.database import NoResultFound, select
from tf2mon.steamplayer import SteamPlayer


def test_select_all(session):
    stmt = select(SteamPlayer)
    for steamplayer in session.scalars(stmt):
        print(steamplayer)


def test_select_not_found(session):
    stmt = select(SteamPlayer).where(SteamPlayer.steamid == -123)
    result = session.scalars(stmt)
    with pytest.raises(NoResultFound):
        print(result.one())


def _test_select_find_one(session):
    stmt = select(SteamPlayer).where(SteamPlayer.steamid == 42708103)
    result = session.scalars(stmt)
    print(result.one())
