"""Logger controls."""

from enum import Enum

from loguru import logger as _logger

import tf2mon
from tf2mon.control import Control, CycleControl
from tf2mon.toggle import Toggle


class LogLevelControl(CycleControl):
    """Cycle logger `level`."""

    name = "TOGGLE-LOG-LEVEL"
    enum = Enum("_e_loglvl", "INFO DEBUG TRACE")
    toggle = Toggle("_t_loglvl", enum)
    items = {
        enum.INFO: "INFO",  # ""
        enum.DEBUG: "DEBUG",  # "-v"
        enum.TRACE: "TRACE",  # "-vv"
    }

    def start(self) -> None:
        """Set logging level based on `--verbose`."""

        tf2mon.ui.logsink.set_verbose(tf2mon.options.verbose)
        self.toggle.start(self.enum.__dict__[tf2mon.ui.logsink.level])

    def handler(self, _match) -> None:
        tf2mon.ui.logsink.set_level(self.items[self.toggle.cycle])
        tf2mon.ui.show_status()


class LogLocationControl(CycleControl):
    """Cycle logger `location` format."""

    name = "TOGGLE-LOG-LOCATION"
    enum = Enum("_e_logloc", "MOD NAM THM THN FILE NUL")
    toggle = Toggle("_t_logloc", enum)
    items = {
        enum.MOD: "{module}.{function}:{line}",
        enum.NAM: "{name}.{function}:{line}",
        enum.THM: "{thread.name}:{module}.{function}:{line}",
        enum.THN: "{thread.name}:{name}.{function}:{line}",
        enum.FILE: "{file}:{function}:{line}",
        enum.NUL: None,
    }

    def start(self) -> None:
        self.toggle.start(self.enum.__dict__[tf2mon.options.log_location])
        tf2mon.ui.logsink.set_location(self.items[self.toggle.value])

    def handler(self, _match) -> None:
        tf2mon.ui.logsink.set_location(self.items[self.toggle.cycle])
        tf2mon.ui.show_status()

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


class ResetPaddingControl(Control):
    """Reset logger `padding`."""

    name = "RESET-PADDING"

    def handler(self, _match) -> None:
        tf2mon.ui.logsink.reset_padding()
        _logger.info("padding reset")
