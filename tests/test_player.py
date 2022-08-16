import pytest

from tf2mon.player import Player

# pylint: disable=unused-argument


def test_valueholders_cls():
    assert Player.valueholders() == "values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"


def test_valueholders_obj():
    assert Player(0).valueholders() == "values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"


def _test_select_all(session):
    for player in Player.select_all():
        print(player)


@pytest.mark.parametrize(("steamid"), [-3, -2, -1, 0, 1, 2, 3])
def test_select_not_found(session, steamid):
    assert Player.lookup_steamid(steamid) is None


@pytest.mark.parametrize(("steamid"), [4377])
def test_select_found(session, steamid):
    player = Player.lookup_steamid(steamid)
    assert player
    # print(player)
