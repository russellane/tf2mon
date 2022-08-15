"""Database."""

import logging

from loguru import logger
from sqlalchemy import Column, Integer, String, create_engine, inspect, select  # noqa
from sqlalchemy.exc import NoResultFound  # noqa
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker


class Base:
    """Augment tables with a `repr`."""

    @property
    def asdict(self):
        """Docstring."""
        return {x.key: getattr(self, x.key) for x in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return f"{self.__class__.__name__}({self.asdict})"


Base = declarative_base(cls=Base)

SESSION = None


def Session(path=None) -> object:  # noqa invalid-name
    """Open and return new session with database."""

    global SESSION  # pylint: disable=global-statement
    if not SESSION and path:

        uri = f"sqlite:///{path}"
        logger.info(f"Opening `{uri}`")
        engine = create_engine(uri, echo=False, future=True)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        SESSION = scoped_session(sessionmaker(bind=engine))
        Base.metadata.create_all(engine)

    return SESSION()
