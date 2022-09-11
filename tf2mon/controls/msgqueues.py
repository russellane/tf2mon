"""Message queues control."""

from pathlib import Path
from typing import IO, Callable

from tf2mon.control import Control


class MsgQueuesControl(Control):
    """Message queues control."""

    path: Path = None
    _controls: list[Control] = []
    _file: IO[str] = None

    def open(self, path: Path) -> None:

        self.path = path

        if path and path.parent.is_dir():
            # pylint: disable=consider-using-with
            self._file = open(path, "w", encoding="utf-8")  # noqa

    # append: Callable[[Control], None] = _controls.append

    def append(self, control: Callable[[Control], None]) -> None:
        """Add `control` to the collection."""
        self._controls.append(control)

    def clear(self) -> None:
        """Clear all message queues."""

        for control in self._controls:
            control.clear()

    def send(self) -> None:
        """Send data to tf2 by writing aliases to an `exec` script."""

        if not self._file:
            return

        self._file.seek(0)
        self._file.truncate()
        for control in self._controls:
            print("\n".join(control.aliases()), file=self._file)
        self._file.flush()
