from tests.apps.prefix.controls import Television


class TelevisionVolume(Television):
    def handler(self) -> None:
        print(self)
