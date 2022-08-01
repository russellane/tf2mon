"""Docstring."""

from sqlalchemy import Column, Integer, String, inspect

from tf2mon.database import Base


class Player(Base):
    """Docstring."""

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

    @property
    def asdict(self):
        """Docstring."""
        return {x.key: getattr(self, x.key) for x in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return f"{self.__class__.__name__}({self.asdict})"


if __name__ == "__main__":
    print(Player().asdict)
