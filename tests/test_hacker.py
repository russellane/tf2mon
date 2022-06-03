from pathlib import Path

import icecream
import pytest
from icecream import ic

from tf2mon.hacker import HackerManager

icecream.ic.configureOutput(prefix="=====>\n", includeContext=True)
CACHE = Path.home() / ".cache" / "tf2mon"
BASE = CACHE / "playerlist.milenko-list.json"
LOCAL = CACHE / "playerlist.tf2mon-list.json"
# pylint: disable=protected-access
# pylint: disable=using-constant-test

disabled = pytest.mark.skipif(True, reason="disabled")


# @disabled
def test_print_hacker_names():
    hackers = HackerManager(base=BASE, local=LOCAL)
    print(f"combined: there are {len(hackers._hackers_by_name):3} names")
    for name, list_of_hackers in hackers._hackers_by_name.items():
        print(f"combined: len={len(list_of_hackers):3} name=`{name}`")
        # for hacker in list_of_hackers:
        #    ic(hacker)


@disabled
def test_print_base_hacker_names():
    hackers = HackerManager(base=BASE)
    print(f"base: there are {len(hackers._hackers_by_name):3} names")
    for name, list_of_hackers in hackers._hackers_by_name.items():
        print(f"base: len={len(list_of_hackers):3} name=`{name}`")


@disabled
def test_print_local_hacker_names():
    hackers = HackerManager(local=LOCAL)
    print(f"local: there are {len(hackers._hackers_by_name):3} names")
    for name, list_of_hackers in hackers._hackers_by_name.items():
        print(f"local: len={len(list_of_hackers):3} name=`{name}`")


@disabled
def test_hacker():

    hackers = HackerManager(base=None, local=LOCAL)

    if False:
        for k, v in hackers._hackers_by_name.items():
            ic(k)
            for i in v:
                ic(i)

    if False:
        for k, v in hackers._hackers_by_steamid.items():
            print(f"k={k} v={v}")

    if False:
        for hacker in hackers._hackers_by_name.values():
            ic(hacker)

    if False:
        for hacker in hackers._hackers_by_steamid.values():
            ic(hacker)
