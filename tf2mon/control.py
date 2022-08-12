"""Application control."""

from tf2mon.command import CommandManager


class Control:
    """Application control."""

    # Controls are created before the monitor and its ui.
    monitor = None


class BoolControl(Control):
    """Bool control."""

    toggle = None

    def handler(self, _match) -> None:
        """Handle event."""

        if self.monitor.toggling_enabled:
            _ = self.toggle.toggle
            self.monitor.ui.show_status()

    def status(self) -> str:
        """Return value formatted for display."""

        return self.toggle.name.upper() if self.toggle.value else self.toggle.name

    @property
    def value(self) -> bool:
        """Return value."""

        return self.toggle.value


class ControlManager:
    """Collection of `Control`s."""

    items: dict[str, Control] = {}
    commands = CommandManager()

    # def __call__(self) -> dict[str, Control]:
    #     """Return collection of `Control`s."""

    #     return self.items

    def __getitem__(self, name: str) -> Control:
        """Return the `Control` known as `name`."""

        return self.items[name]

    def add(self, control: Control) -> None:
        """Add `control`, known as its class name, to collection."""

        self.items[control.__class__.__name__] = control

    def bind(self, name: str, keyspec: str = None, game_only: bool = False) -> None:
        """Bind the control known as `name` to `keyspec`."""

        self.commands.bind(self.items[name], keyspec, game_only)

    def add_arguments_to(self, parser) -> None:
        """Add arguments for all controls to `parser`."""

        for control in self.items.values():
            if hasattr(control, "add_arguments_to"):
                control.add_arguments_to(parser)
