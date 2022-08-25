from tests.apps.both.controls import TelevisionControl


class TelevisionVolumeControl(TelevisionControl):
    def handler(self) -> None:
        print(self)
