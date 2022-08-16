import pytest  # noqa: unused-import

from tf2mon.player import Player


def test_select_all(session):  # noqa: unused-argument
    for player in Player.select_all():
        print(player)


def test_select_not_found(session):  # noqa: unused-argument
    assert Player.lookup_steamid(-123) is None


def test_select_find_one(session):  # noqa: unused-argument
    player = Player.lookup_steamid(4377)
    assert player
    print(player)
