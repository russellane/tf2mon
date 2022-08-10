import pytest

from tf2mon.database import Session


@pytest.fixture(scope="session")
def session():

    return Session(".cache/tf2mon.db")
