import pytest

from tf2mon.steamplayer import SteamPlayer

# pylint: disable=unused-argument

VALUEHOLDERS = "values(?,?,?,?,?,?,?,?,?,?)"


def test_valueholders_cls():
    assert SteamPlayer.valueholders() == VALUEHOLDERS


def test_valueholders_obj():
    assert SteamPlayer(0).valueholders() == VALUEHOLDERS


def _test_select_all(session):
    for result in SteamPlayer.select_all():
        print(result)


@pytest.mark.parametrize(("steamid"), [-3, -2, -1, 0, 1])
def test_fetch_steamid_not_found(session, steamid):
    assert SteamPlayer.fetch_steamid(steamid) is None


@pytest.mark.parametrize(("steamid"), [42708103])
def _test_fetch_steamid_found(session, steamid):
    result = SteamPlayer.fetch_steamid(steamid)
    assert result
    print(result)
