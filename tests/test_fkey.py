import string

import icecream  # type: ignore
import pytest
from icecream import ic

from tf2mon.fkey import FKey

icecream.install()
icecream.ic.configureOutput(prefix="=====>\n", includeContext=True)


@pytest.mark.parametrize(
    ("keyspec"),
    [
        None,
        "",
        "shift",
        "shift+",
        "ctrl",
        "ctrl+",
        "shif+A",
        "ctr+A",
        "ctrl+shift",
        "ctrl+shift+",
        "ctrl+shift+A",
        "+A",
        "+shift+A",
        "+ctrl+A",
    ],
)
def test_fkey_value_error(keyspec: str) -> None:

    with pytest.raises(ValueError, match="keyspec") as err:
        FKey(keyspec)
    assert err.type == ValueError


@pytest.mark.parametrize(
    ("keyspec", "key", "is_shift", "is_ctrl"),
    [(x, ord(x), False, False) for x in string.ascii_uppercase]
    + [(x, ord(x) - (ord("a") - ord("A")), False, False) for x in string.ascii_lowercase]
    + [(f"shift+{x}", ord(x), True, False) for x in string.ascii_uppercase]
    + [
        (f"shift+{x}", ord(x) - (ord("a") - ord("A")), True, False)
        for x in string.ascii_lowercase
    ]
    + [(f"ctrl+{x}", ord(x), False, True) for x in string.ascii_uppercase]
    + [
        (f"ctrl+{x}", ord(x) - (ord("a") - ord("A")), False, True)
        for x in string.ascii_lowercase
    ],
)
def test_fkey_letters(keyspec: str, key: int, is_shift: bool, is_ctrl: bool) -> None:

    keystroke = ic(FKey(keyspec))
    assert keystroke.key == key
    assert keystroke.is_shift is is_shift
    assert keystroke.is_ctrl is is_ctrl


def test_fkey_a_A() -> None:

    assert FKey("a").__dict__ == FKey("A").__dict__


def test_fkey_f1_F1() -> None:

    assert FKey("f1").__dict__ == FKey("F1").__dict__


def test_fkey_f1() -> None:

    keystroke = ic(FKey("f1"))
    assert not keystroke.is_shift
    assert not keystroke.is_ctrl


def test_fkey_f12() -> None:

    keystroke = ic(FKey("f12"))
    assert not keystroke.is_shift
    assert not keystroke.is_ctrl


def test_fkey_f13() -> None:

    keystroke = ic(FKey("f13"))
    assert not keystroke.is_shift
    assert not keystroke.is_ctrl


def test_fkey_shift_f1() -> None:

    keystroke = ic(FKey("shift+f1"))
    assert keystroke.is_shift
    assert not keystroke.is_ctrl


def test_fkey_shift_f12() -> None:

    keystroke = ic(FKey("shift+f12"))
    assert keystroke.is_shift
    assert not keystroke.is_ctrl


def test_fkey_shift_f13() -> None:

    keystroke = ic(FKey("shift+f13"))
    assert keystroke.is_shift
    assert not keystroke.is_ctrl


def test_fkey_ctrl_f1() -> None:

    keystroke = ic(FKey("ctrl+f1"))
    assert not keystroke.is_shift
    assert keystroke.is_ctrl


def test_fkey_ctrl_f12() -> None:

    keystroke = ic(FKey("ctrl+f12"))
    assert not keystroke.is_shift
    assert keystroke.is_ctrl


def test_fkey_ctrl_f13() -> None:

    keystroke = ic(FKey("ctrl+f13"))
    assert not keystroke.is_shift
    assert keystroke.is_ctrl
