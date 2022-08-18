"""Cycle logger `location` format."""

from enum import Enum

import tf2mon
from tf2mon.control import CycleControl
from tf2mon.toggle import Toggle


class LogLocationControl(CycleControl):
    """Cycle logger `location` format."""

    name = "TOGGLE-LOG-LOCATION"
    enum = Enum(f"_e_{name}", "MOD NAM THM THN FILE NUL")
    toggle = Toggle(f"_t_{name}", enum)
    items = {
        enum.MOD: "{module}.{function}:{line}",
        enum.NAM: "{name}.{function}:{line}",
        enum.THM: "{thread.name}:{module}.{function}:{line}",
        enum.THN: "{thread.name}:{name}.{function}:{line}",
        enum.FILE: "{file}:{function}:{line}",
        enum.NUL: None,
    }

    #
    def start(self, value: str) -> None:
        self.toggle.start(self.enum.__dict__[value])
        tf2mon.monitor.ui.logsink.set_location(self.items[self.toggle.value])

    def handler(self, _match) -> None:
        tf2mon.monitor.ui.logsink.set_location(self.items[self.toggle.cycle])
        tf2mon.monitor.ui.show_status()

    def status(self) -> str:
        return self.toggle.value.name

    def add_arguments_to(self, parser) -> None:
        arg = parser.add_argument(
            "--log-location",
            choices=[x.name for x in list(self.enum)],
            default="NUL",
            help="choose format of logger location field",
        )
        self.add_fkey_to_help(arg)
        self.cli.add_default_to_help(arg)
