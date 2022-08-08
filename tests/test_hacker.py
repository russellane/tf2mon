from pathlib import Path

from tf2mon.hacker import HackerManager

DBFILE = Path.home() / ".cache" / "tf2mon" / "hackers.json"


def test_hacker():
    hackers = HackerManager(DBFILE)
    # print(f"there are {len(hackers()):3} steamids")
    for _hacker in sorted(hackers().values(), key=lambda x: x.last_time, reverse=True):
        pass  # print(hacker)
