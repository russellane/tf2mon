import pytest

from tf2mon.database import open_database_session


@pytest.fixture(scope="session")
def session():

    return open_database_session(".cache/tf2mon.db")
