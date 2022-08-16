import pytest

from tf2mon.database import Database


@pytest.fixture(scope="session")
def session():

    return Database(".cache/tf2mon.db")
