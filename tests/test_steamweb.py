import logging
from pathlib import Path

import pytest
import tomli

from tf2mon.steamplayer import SteamPlayer
from tf2mon.steamweb import SteamWebAPI

logging.basicConfig(force=True, level=logging.DEBUG)


@pytest.fixture(name="api", scope="session")
def api_(session: str) -> SteamWebAPI:
    # pylint: disable=unused-argument

    path = Path("~/.tf2mon.toml").expanduser()
    config = tomli.loads(path.read_text(encoding="utf-8"))
    webapi_key = None
    tf2mon = config.get("tf2mon")
    assert tf2mon
    webapi_key = tf2mon.get("webapi_key")
    return SteamWebAPI(webapi_key)


@pytest.mark.parametrize(("steamid"), [-3, -2, -1, 0])
def test_fetch_steamid_not_found(api: SteamWebAPI, steamid: int) -> None:
    result = api.fetch_steamid(steamid)
    # print(result)
    assert result
    assert result.personaname == "???"


@pytest.mark.parametrize(
    ("steamid", "expected"),
    [
        (
            2,
            SteamPlayer(
                steamid=2,
                personaname="alfred",
                profileurl="https://steamcommunity.com/id/zoe/",
                personastate=0,
                realname="Alfred",
                timecreated=1063193241,
                loccountrycode="",
                locstatecode="",
                loccityid="",
            ),
        ),
    ],
)
def test_fetch_known_steamids(api: SteamWebAPI, steamid: int, expected: SteamPlayer) -> None:
    result = api.fetch_steamid(steamid)
    assert result
    assert result.steamid == expected.steamid
    assert result.personaname == expected.personaname
    assert result.profileurl == expected.profileurl
    assert result.personastate == expected.personastate
    assert result.realname == expected.realname
    assert result.timecreated == expected.timecreated
    assert result.loccountrycode == expected.loccountrycode
    assert result.locstatecode == expected.locstatecode
    assert result.loccityid == expected.loccityid
    # assert result.mtime == expected.mtime
    # print(f"result={result}")


@pytest.mark.parametrize(("steamid"), [42708103])
def test_fetch_steamid_found(api: SteamWebAPI, steamid: int) -> None:
    steamplayer = api.fetch_steamid(steamid)
    assert steamplayer
    # print(steamplayer)
