"""Show debug control."""

from tf2mon.command import Command
from tf2mon.control import Control
from tf2mon.toggle import Toggle


class ShowDebugControl(Control):
    """Show debug control."""

    name = "SHOW-DEBUG"

    TOGGLE = Toggle("_df", [False, True])

    def handler(self, _match) -> None:
        """Handle event."""

        self.monitor.ui.show_debug()

    def command(self) -> Command:
        """Create and return `Command` object for this control."""

        return Command(
            name=self.name,
            handler=self.handler,
        )
