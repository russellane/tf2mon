"""Database."""

import dataclasses
import sqlite3
from typing import Iterator

from loguru import logger

DATABASE = None


def Database(path=None, tables=None) -> sqlite3.dbapi2.Cursor:  # noqa invalid-name
    """Open and return new session with database."""

    global DATABASE  # pylint: disable=global-statement
    if not DATABASE and path:

        logger.info(f"Opening `{path}`")
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        DATABASE = conn.cursor()

        for table in tables or []:
            table.create_table()

    return DATABASE


class DatabaseTable:
    """Base class for all database tables."""

    __tablename__: str = None

    @classmethod
    def select_all(cls) -> Iterator[object]:
        """Yield all rows in table."""

        for row in Database().execute(f"select * from {cls.__tablename__}"):
            yield cls(*tuple(row))

    @classmethod
    def valueholders(cls) -> str:
        """Return text for sql `values` clause."""

        placeholders = ",".join(["?"] * len(dataclasses.fields(cls)))
        return f"values({placeholders})"

    def astuple(self) -> tuple:
        """Return column values."""

        return dataclasses.astuple(self)

    def upsert(self) -> None:
        """Update or Insert this row into the table."""

        try:
            Database().execute(
                f"replace into {self.__tablename__} {self.valueholders()}",
                self.astuple(),
            )
        except Exception as err:
            logger.critical(err)
            raise
        Database().connection.commit()
