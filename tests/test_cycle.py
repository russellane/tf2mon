import pytest

from tf2mon.cycle import Cycle


def test_prev() -> None:
    cycle = Cycle("numbers", ["one", "two", "three", "four", "five"])
    assert cycle.value == "one"
    assert cycle.prev == "five"
    assert cycle.prev == "four"
    assert cycle.prev == "three"
    assert cycle.prev == "two"
    assert cycle.prev == "one"
    assert cycle.prev == "five"
    assert cycle.value == "five"


def test_next() -> None:
    cycle = Cycle("numbers", ["one", "two", "three", "four", "five"])
    assert cycle.value == "one"
    assert cycle.next == "two"
    assert cycle.next == "three"
    assert cycle.next == "four"
    assert cycle.next == "five"
    assert cycle.next == "one"
    assert cycle.next == "two"
    assert cycle.value == "two"


def test_getitem() -> None:
    cycle = Cycle("numbers", ["one", "two", "three", "four", "five"])
    assert cycle[0] == "one"
    assert cycle[1] == "two"
    assert cycle[2] == "three"
    assert cycle[3] == "four"
    assert cycle[4] == "five"
    assert cycle[-1] == "five"
    assert cycle[-5] == "one"

    with pytest.raises(IndexError):
        _ = cycle[5]
    with pytest.raises(IndexError):
        _ = cycle[-6]


def test_start() -> None:
    cycle = Cycle("numbers", ["one", "two", "three", "four", "five"])
    cycle.start("one")
    assert cycle.value == "one"
    cycle.start("two")
    assert cycle.value == "two"
    cycle.start("three")
    assert cycle.prev == "two"
    cycle.start("four")
    assert cycle.next == "five"
    cycle.start("five")
    assert cycle.value == "five"

    with pytest.raises(KeyError):
        cycle.start("zero")
    with pytest.raises(KeyError):
        cycle.start("")
    with pytest.raises(KeyError):
        cycle.start(None)
