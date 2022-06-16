from tf2mon.conlog import Conlog


def test_one():

    print()
    conlog = Conlog("tests/data/bot-chain", rewind=True, follow=False)
    conlog.open()
    for line in conlog.readline():
        print(f"line={line!r}")
