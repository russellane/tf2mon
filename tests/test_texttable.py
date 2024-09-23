# import pytest

from tf2mon.texttable import TextColumn, TextTable


def test_column() -> None:

    table = TextTable(
        [
            TextColumn(-10, "STEAMID"),
            TextColumn(4.1, "KD"),
            TextColumn(-4, "AGE"),
            TextColumn(1, "P"),
            TextColumn(2, "CC"),
            TextColumn(2, "SC"),
            TextColumn(4, "CI"),
            TextColumn(25, "PERSONANAME"),
            TextColumn(0, "REALNAME"),
        ]
    )

    assert (
        table.formatted_header
        == "   STEAMID   KD  AGE P CC SC CI   PERSONANAME               REALNAME"
    )

    assert (
        table.format_detail(
            12345,
            3.14159,
            5000,
            "1",
            "2",
            "3",
            "4",
            "Persona Name",
            "Real Name",
        )
        == "     12345  3.1 5000 1 2  3  4    Persona Name              Real Name"
    )
