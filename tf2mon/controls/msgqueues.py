"""Message queues control."""

from pathlib import Path
from typing import IO, Match

from loguru import logger

import tf2mon
from tf2mon.control import Control


class MsgQueuesControl(Control):
    """Message queues control."""

    _controls: list[Control] = []
    _file: IO[str] | None = None

    def start(self) -> None:
        """Complete initialization; post CLI, options now available."""

        self._controls.append(tf2mon.KicksControl)
        self._controls.append(tf2mon.SpamsControl)

        # Location of TF2 `exec` scripts.
        _scripts = tf2mon.options.tf2_install_dir / "cfg" / "user"

        # MsgQueue aliases; written often; left open.
        _dynamic_path = _scripts / "tf2mon-pull.cfg"

        # Static aliases and key bindings; written once (now).
        _static_path = _scripts / "tf2mon.cfg"

        if not _scripts.is_dir():
            logger.warning(f"Can't find scripts dir `{_scripts}`")
            logger.warning(f"Not opening `{_dynamic_path}`")
            logger.warning(f"Not writing `{_static_path}`")
            return

        logger.info(f"Writing `{_static_path}`")
        script = tf2mon.controller.as_tf2_exec_script(
            str(_static_path.relative_to(_scripts.parent)),
            str(_dynamic_path.relative_to(_scripts.parent)),
        )
        _static_path.write_text(script, encoding="utf-8")

        logger.info(f"Opening `{_dynamic_path}`")
        # pylint: disable=consider-using-with
        self._file = open(_dynamic_path, "w", encoding="utf-8")  # noqa

    def clear(self) -> None:
        """Clear all message queues."""

        for control in self._controls:
            assert hasattr(control, "clear")
            control.clear()

    def send(self) -> None:
        """Send data to tf2 by writing aliases to an `exec` script."""

        if not self._file:
            return

        self._file.seek(0)
        self._file.truncate()
        for control in self._controls:
            assert hasattr(control, "aliases")
            print("\n".join(control.aliases()), file=self._file)
        self._file.flush()


class DisplayFileControl(Control):
    """Display file."""

    name = "DISPLAY-FILE"
    _path: Path | None = None

    def start(self) -> None:
        self._path = tf2mon.options.tf2_install_dir / "cfg" / "user" / "tf2mon.cfg"

    def handler(self, _match: Match[str] | None) -> None:

        assert self._path
        tf2mon.ui.popup(
            "help",
            f" {self._path} ".center(80, "-") + "\n" + self._path.read_text(encoding="utf-8"),
        )
