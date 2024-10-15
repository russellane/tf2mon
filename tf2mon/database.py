"""Database."""

from __future__ import annotations

import dataclasses
import sqlite3
from pathlib import Path
from typing import Any, Iterator

from loguru import logger

DATABASE: sqlite3.dbapi2.Cursor | None = None


def Database(  # pylint: disable=invalid-name
    path: Path | None = None,
    tables: list[type[DatabaseTable]] | None = None,
) -> sqlite3.dbapi2.Cursor | None:  # noqa invalid-name
    """Open and return new session with database."""

    global DATABASE  # pylint: disable=global-statement
    if not DATABASE and path:

        _path = path.expanduser()
        logger.info(f"Opening `{_path}`")
        conn = sqlite3.connect(_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        DATABASE = conn.cursor()

        for table in tables or []:
            table.create_table()

    return DATABASE


class DatabaseTable:
    """Base class for all database tables."""

    __tablename__: str

    @classmethod
    def create_table(cls) -> None:
        """Docstring."""

        raise NotImplementedError

    @classmethod
    def select_all(cls) -> Iterator[object]:
        """Yield all rows in table."""

        db = Database()
        assert db

        for row in db.execute(f"select * from {cls.__tablename__}"):
            yield cls(*tuple(row))

    @classmethod
    def valueholders(cls) -> str:
        """Return text for sql `values` clause."""

        placeholders = ",".join(["?"] * len(dataclasses.fields(cls)))  # type: ignore
        return f"values({placeholders})"

    def astuple(self) -> tuple[Any, ...]:
        """Return column values."""

        return dataclasses.astuple(self)  # type: ignore

    def upsert(self) -> None:
        """Update or Insert this row into the table."""

        db = Database()
        assert db

        try:
            db.execute(
                f"replace into {self.__tablename__} {self.valueholders()}",
                self.astuple(),
            )
        except Exception as err:
            logger.critical(err)
            raise
        db.connection.commit()
