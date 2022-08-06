"""Database."""

from loguru import logger
from sqlalchemy import Column, Integer, String, create_engine, inspect, select  # noqa
from sqlalchemy.exc import NoResultFound  # noqa
from sqlalchemy.orm import Session, declarative_base


class Base:
    """Augment tables with a `repr`."""

    @property
    def asdict(self):
        """Docstring."""
        return {x.key: getattr(self, x.key) for x in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return f"{self.__class__.__name__}({self.asdict})"


Base = declarative_base(cls=Base)


def open_database_session(path) -> Session:
    """Open and return new session with database."""

    uri = f"sqlite:///{path}"
    logger.info(f"Opening {uri}")
    engine = create_engine(uri, echo=False, future=True)
    session = Session(engine)
    Base.metadata.create_all(engine)
    return session
