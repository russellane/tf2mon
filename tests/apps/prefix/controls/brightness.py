from tests.apps.prefix.controls import Television


class TelevisionBrightness(Television):
    def handler(self) -> None:
        print(self)
