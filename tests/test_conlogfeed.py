import sys
from collections import namedtuple
from queue import SimpleQueue

import pytest
from loguru import logger

from tests.testlib import slow
from tf2mon.conlogfeed import ConlogFeed

DataFile = namedtuple("datafile", ["nlines", "path"])
Null = DataFile(0, "/dev/null")
Small = DataFile(12, "tests/data/bot-chain")
Large = DataFile(1140, "tests/data/bots-orig")


@pytest.mark.parametrize(
    ("name", "nlines", "path", "rewind", "follow"),
    [
        ("--rewind", Null.nlines, Null.path, True, False),
        ("--rewind", Small.nlines, Small.path, True, False),
        ("--no-rewind", Null.nlines, Null.path, False, False),
        ("--no-rewind", Small.nlines, Small.path, False, False),
        ("--no-rewind", Large.nlines, Large.path, False, False),
    ],
)
def test_queue_get(name, nlines, path, rewind, follow):

    _ = name  # unused
    print(file=sys.stderr, flush=True)
    feed = ConlogFeed(SimpleQueue(), path, rewind=rewind, follow=follow)
    feed.debug = True
    last_lineno = None

    while True:
        (msgtype, lineno, line) = feed.queue.get()
        logger.debug(f"msgtype {msgtype} lineno {lineno} line `{line.strip()}`")
        if lineno <= 0:
            break
        last_lineno = lineno

    assert feed.lineno == nlines
    if last_lineno is not None:
        assert last_lineno == nlines

    logger.debug(f"NLINES: {nlines}")


@slow
@pytest.mark.parametrize(
    ("name", "nlines", "path", "rewind", "follow"),
    [
        ("--rewind", Large.nlines, Large.path, True, False),
    ],
)
def test_queue_get_slow(name, nlines, path, rewind, follow):
    test_queue_get(name, nlines, path, rewind, follow)
