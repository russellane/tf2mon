from tf2mon.importer import Importer


def test_game():
    print()
    importer = Importer("tf2mon.game", prefix="Game", suffix="Event")
    print(importer)
