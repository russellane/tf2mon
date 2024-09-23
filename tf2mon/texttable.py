"""Table/Column formatters."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TextColumn:
    """Column formatter."""

    width: int | float
    heading: str
    fmt_heading: str = field(default_factory=str, init=False)
    fmt_detail: str = field(default_factory=str, init=False)

    def __post_init__(self) -> None:
        """Init table column."""

        if isinstance(self.width, float):
            _width, _precision = [int(x) for x in str(self.width).split(".")]
            self.width = _width
            _right = True
        elif isinstance(self.width, int):
            _precision = None
            if self.width < 0:
                _width = self.width = abs(self.width)
                _right = True
            else:
                _width = self.width
                _right = False
        else:
            raise TypeError("width must be int|float")

        # build format string for the header
        self.fmt_heading = "{:"
        if _right:
            self.fmt_heading += ">"
        self.fmt_heading += str(_width) + "}"

        # build format string for the detail
        self.fmt_detail = "{:"
        if _right:
            self.fmt_detail += ">"
        self.fmt_detail += str(_width)
        if _precision:
            self.fmt_detail += f".{_precision}f"
        self.fmt_detail += "}"


@dataclass
class TextTable:
    """Table formatter."""

    columns: list[TextColumn] = field(default_factory=list)
    _formatted_header: str = field(default_factory=str, init=False)
    _fmt_detail: str = field(default_factory=str, init=False)

    @property
    def formatted_header(self) -> str:
        """Docstring."""

        if not self._formatted_header:
            fmt = " ".join([x.fmt_heading for x in self.columns])
            self._formatted_header = fmt.format(*[x.heading for x in self.columns])

        return self._formatted_header

    def format_detail(self, *values: Any) -> str:
        """Docstring."""

        result = []
        for column, value in zip(self.columns, values):
            if value is None:
                result.append(column.fmt_heading.format(""))
            else:
                result.append(column.fmt_detail.format(value))

        return " ".join(result)
