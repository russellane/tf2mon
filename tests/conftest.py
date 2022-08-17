import pytest

from tf2mon.database import Database
from tf2mon.player import Player
from tf2mon.steamplayer import SteamPlayer


@pytest.fixture(scope="session")
def session():

    return Database(".cache/tf2mon.db", [Player, SteamPlayer])
