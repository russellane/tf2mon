"""Database."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()

from loguru import logger


def open_database_session(path):
    """Open and return new session with database."""

    uri = f"sqlite:///{path}"
    logger.info(f"Opening {uri}")
    engine = create_engine(uri, echo=True, future=True)
    session = Session(engine)
    Base.metadata.create_all(engine)
    return session
