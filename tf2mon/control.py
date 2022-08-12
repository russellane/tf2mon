"""Application control."""

from tf2mon.command import CommandManager


class Control:
    """Application control."""

    # Controls are created before the monitor and its ui.
    monitor = None

    @staticmethod
    def status_on_off(key, value):
        """Docstring."""

        return key.upper() if value else key


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
