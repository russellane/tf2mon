import pytest

from tf2mon.player import Player

# pylint: disable=unused-argument

VALUEHOLDERS = "values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"


def test_valueholders_cls() -> None:
    assert Player.valueholders() == VALUEHOLDERS


def test_valueholders_obj() -> None:
    assert Player(0).valueholders() == VALUEHOLDERS


def _test_select_all(session: str) -> None:
    for result in Player.select_all():
        print(result)


@pytest.mark.parametrize(("steamid"), [-3, -2, -1, 0, 1])
def test_fetch_steamid_not_found(session: str, steamid: int) -> None:
    assert Player.fetch_steamid(steamid) is None


@pytest.mark.parametrize(("steamid"), [4377])
def _test_fetch_steamid_found(session: str, steamid: int) -> None:
    result = Player.fetch_steamid(steamid)
    assert result
    print(result)
