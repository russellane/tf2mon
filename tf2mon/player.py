"""Table of `Player`s."""

from tf2mon.database import Base, Column, Integer, String


class Player(Base):
    """A `Player`."""

    __tablename__ = "players"

    # key
    steamid = Column(Integer, primary_key=True)

    # defcon6
    bot = Column(String)
    friends = Column(String)
    tacobot = Column(String)
    pazer = Column(String)

    # playerlist.official
    _cheater = Column(String)
    _suspect = Column(String)
    _exploiter = Column(String)
    _racist = Column(String)
    _last_name = Column(String)
    _s_last_time = Column(String)

    # tf2mon
    cheater = Column(String)
    suspect = Column(String)
    exploiter = Column(String)
    racist = Column(String)
    milenko = Column(Integer)
    last_name = Column(String)
    s_last_time = Column(String)
    names = Column(String)

    def setattrs(self, attrs) -> None:
        """Docstring."""
        for attr in attrs:
            setattr(self, attr, attr)
