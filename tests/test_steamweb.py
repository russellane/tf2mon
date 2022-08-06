from pathlib import Path

import pytest
import tomli

from tf2mon.steamid import SteamID
from tf2mon.steamweb import SteamWebAPI


@pytest.fixture(name="api", scope="session")
def api_(session):
    path = Path("~/.tf2mon.toml").expanduser()
    config = tomli.loads(path.read_text(encoding="utf-8"))
    webapi_key = None
    if tf2mon := config.get("tf2mon"):
        webapi_key = tf2mon.get("webapi_key")
    return SteamWebAPI(webapi_key, session)


def test_find_steamid_1(api):
    steamplayer = api.find_steamid(SteamID(42708103))
    assert steamplayer.steamid == 42708103
    print(steamplayer)


def test_find_steamid_2(api):
    steamplayer = api.find_steamid(SteamID(123))
    assert steamplayer.steamid == 123
    print(steamplayer)


def test_no_find_steamid_1(api):
    steamplayer = api.find_steamid(SteamID(-99))
    assert steamplayer.steamid == 0
    print(steamplayer)
