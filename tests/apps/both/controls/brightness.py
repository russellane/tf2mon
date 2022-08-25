from tests.apps.both.controls import TelevisionControl


class TelevisionBrightnessControl(TelevisionControl):
    def handler(self) -> None:
        print(self)
