from tests.apps.suffix.controls import Control


class VolumeControl(Control):
    def handler(self) -> None:
        print(self)
