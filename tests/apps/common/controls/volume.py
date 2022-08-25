from tests.apps.common.controls import BaseControl


class Control(BaseControl):
    def handler(self) -> None:
        print(self)
