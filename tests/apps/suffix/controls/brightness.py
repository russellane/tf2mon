from tests.apps.suffix.controls import Control


class BrightnessControl(Control):
    def handler(self) -> None:
        print(self)
