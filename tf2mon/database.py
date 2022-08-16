"""Database."""

import dataclasses
import sqlite3

from loguru import logger

DATABASE = None


def Database(path=None) -> object:  # noqa invalid-name
    """Open and return new session with database."""

    global DATABASE  # pylint: disable=global-statement
    if not DATABASE and path:

        logger.info(f"Opening `{path}`")
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        DATABASE = conn.cursor()

    return DATABASE


class DatabaseTable:
    """Base class for all database tables."""

    @classmethod
    def valueholders(cls) -> str:
        """Return text for sql `values` clause."""

        placeholders = ",".join(["?"] * len(dataclasses.fields(cls)))
        return f"values({placeholders})"

    def astuple(self) -> tuple:
        """Return column values."""

        return dataclasses.astuple(self)
