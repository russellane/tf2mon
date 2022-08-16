import pytest

from tf2mon.steamid import SteamID
from tf2mon.steamplayer import SteamPlayer

# pylint: disable=unused-argument


def test_valueholders_cls():
    assert SteamPlayer.valueholders() == "values(?,?,?,?,?,?,?,?,?,?,?)"


def test_valueholders_obj():

    steamplayer = SteamPlayer(
        {
            "steamid": 123,
            "personaname": "FredK",
            "profileurl": "https://steamcommunity.com/id/fredk/",
            "personastate": "0",
            "realname": "Fred Kilbourn",
            "timecreated": 1063251886,
            "loccountrycode": "US",
            "locstatecode": "IL",
            "loccityid": None,
            "mtime": 1660664987,
            "age": 6914,
        },
    )

    assert steamplayer.valueholders() == "values(?,?,?,?,?,?,?,?,?,?,?)"


def _test_select_all(session):
    for steamplayer in SteamPlayer.select_all():
        print(steamplayer)


@pytest.mark.parametrize(("steamid"), [-3, -2, -1, 0, 1, 2, 3])
def test_select_not_found(session, steamid):
    assert SteamPlayer.find_steamid(SteamID(steamid)) is None


@pytest.mark.parametrize(("steamid"), [42708103])
def test_select_found(session, steamid):
    steamplayer = SteamPlayer.find_steamid(SteamID(steamid))
    assert steamplayer
    # print(steamplayer)
