from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from tf2mon.player import Player


def load_players():
    """Load `Player` records."""

    engine = create_engine("sqlite:///../tf2mon-db/data/database.db", echo=True, future=True)
    with Session(engine) as session:
        stmt = select(Player)
        for player in session.scalars(stmt):
            print(player)


if __name__ == "__main__":
    load_players()
