"""Database."""

import sqlite3

from loguru import logger

DATABASE = None


def Database(path=None) -> object:  # noqa invalid-name
    """Open and return new session with database."""

    global DATABASE  # pylint: disable=global-statement
    if not DATABASE and path:

        logger.info(f"Opening `{path}`")
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        DATABASE = conn.cursor()

    return DATABASE
