"""Globals."""

import curses
from argparse import Namespace
from pprint import pformat

from loguru import logger

from tf2mon._users import Users as users  # noqa: unused-import
from tf2mon.admin import Admin
from tf2mon.conlog import Conlog
from tf2mon.ui import UI
from tf2mon.user import Team

admin: Admin = None
chats: list = []
conlog: Conlog = None
is_single_stepping: bool = None
options: Namespace = None
ui: UI = None


def reset_game():
    """Start new game."""

    logger.success("RESET GAME")

    users.me.assign_team(Team.BLU)
    users.my.display_level = "user"
    global chats  # pylint: disable=global-statement,invalid-name
    chats = []
    ui.refresh_chats()
    # msgqueues.clear()


def toggling_enabled() -> bool:
    """Return True if toggling is enabled.

    Don't allow toggling when replaying a game (`--rewind`),
    unless `--toggles` is also given... or if single-stepping

    This is checked by keys that alter the behavior of gameplay;
    it is not checked by keys that only alter the display.
    """

    return conlog.is_eof or options.toggles or is_single_stepping


def debugger() -> None:
    """Drop into python debugger."""

    if conlog.is_eof or is_single_stepping:
        curses.reset_shell_mode()
        breakpoint()  # pylint: disable=forgotten-debug-statement
        curses.reset_prog_mode()


def dump() -> None:
    """Dump stuff."""

    # logger.success(pformat(self.__dict__))
    logger.success(pformat(users.__dict__))
    for user in users.users_by_username.values():
        logger.success(pformat(user.__dict__))
