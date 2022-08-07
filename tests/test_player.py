import pytest

from tf2mon.database import NoResultFound, select
from tf2mon.player import Player


def test_select_all(session):
    stmt = select(Player)
    for player in session.scalars(stmt):
        print(player)


def test_select_not_found(session):
    stmt = select(Player).where(Player.steamid == -123)
    result = session.scalars(stmt)
    with pytest.raises(NoResultFound):
        print(result.one())


def test_select_find_one(session):
    stmt = select(Player).where(Player.steamid == 4377)
    result = session.scalars(stmt)
    print(result.one())
