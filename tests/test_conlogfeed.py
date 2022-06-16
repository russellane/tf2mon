import sys
import time
from queue import SimpleQueue

from loguru import logger

from tf2mon.conlog import Conlog
from tf2mon.conlogfeed import ConlogFeed

logger.remove(0)
logger.add(
    sys.stderr,
    format="{time:HH:MM:SS} {thread.name} {name}.{function}:{line} {message}",
    level="TRACE",
)

DEBUG = True


def _test_one():

    conlog = Conlog("tests/data/bot-chain", rewind=True, follow=False)
    feed = ConlogFeed(SimpleQueue(), conlog, debug=DEBUG)
    logger.warning("feed.running.SET")
    feed.running.set()
    feed.run()

    conlog.open()
    for line in conlog.readline():
        print(f"line={line!r}")


def test_two():

    print()
    conlog = Conlog("tests/data/bot-1", rewind=True, follow=False)
    feed = ConlogFeed(SimpleQueue(), conlog, debug=DEBUG)
    logger.warning("feed.running.CLEAR")
    feed.running.clear()
    logger.warning("feed.waiting.SET")
    feed.waiting.set()
    feed.run()

    while True:
        logger.debug("feed.running.CLEAR")
        feed.running.clear()

        logger.debug("feed.waiting.WAIT")
        feed.waiting.wait()

        time.sleep(0.1)  # simulate press ENTER

        # Wait for line.
        try:
            (msgtype, *args) = feed.queue.get()
        except KeyboardInterrupt as err:
            logger.error(err)
            break

        logger.debug(f"msgtype={msgtype!r} args={args!r}\n")
        logger.debug("feed.running.SET")
        feed.running.set()
