import pytest  # noqa: unused-import

from tf2mon.steamid import SteamID
from tf2mon.steamplayer import SteamPlayer


def test_select_all(session):  # noqa: unused-argument
    for steamplayer in SteamPlayer.select_all():
        print(steamplayer)


def test_select_not_found(session):  # noqa: unused-argument
    assert SteamPlayer.find_steamid(SteamID(-123)) is None


def test_select_find_one(session):  # noqa: unused-argument
    steamplayer = SteamPlayer.find_steamid(SteamID(42708103))
    assert steamplayer is not None
    print(steamplayer)
