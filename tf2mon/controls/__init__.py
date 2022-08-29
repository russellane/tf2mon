"""Application controls."""

from tf2mon.command import Command, CommandManager
from tf2mon.control import Control
from tf2mon.fkey import FKey
from tf2mon.importer import Importer


class _Controls:
    """Collection of `Control`s."""

    items: dict[str, Control] = {}
    bindings: list[Control] = []

    commands = CommandManager()
    get_regex_list = commands.get_regex_list
    get_status_line = commands.get_status_line

    def __init__(
        self,
        modname: str,
        basename: str = None,
        prefix: str = None,
        suffix: str = None,
    ) -> None:
        """Add all `Control`s in module `modname`."""

        importer = Importer(modname, basename, prefix, suffix)
        for klass in importer.classes.values():
            control = klass()
            self.items[control.__class__.__name__] = control

    def __getitem__(self, name: str) -> Control:
        """Return the `Control` known as `name`."""

        return self.items[name]

    def add(self, control: Control) -> None:
        """Add `control`, known as its class name, to collection."""

        self.items[control.__class__.__name__] = control

    def bind(self, name: str, keyspec: str = None, game_only: bool = False) -> None:
        """Bind the control known as `name` to `keyspec`."""

        handler = "handler"
        if "." in name:
            name, handler = name.split(".", maxsplit=1)

        control = self.items[name]
        self.bindings.append(control)
        control.fkey = FKey(keyspec)

        control.command = Command(
            control.name,
            getattr(control, "status", None),
            getattr(control, handler, None),
            getattr(control, "action", None),
        )
        self.commands.bind(control.command, keyspec, game_only)

    def add_arguments_to(self, parser) -> None:
        """Add arguments for all controls to `parser`."""

        cli = parser.get_default("cli")
        for control in self.items.values():
            if hasattr(control, "add_arguments_to"):
                control.cli = cli
                control.add_arguments_to(parser)

    def fkey_help(self) -> str:
        """Return help for function keys."""

        lines = []
        for control in self.bindings:
            # 17 == indent 4 + len("KP_RIGHTARROW")
            lines.append(f"{control.fkey.keyspec:>17} {control.__doc__}")
        return "\n".join(lines)

    def start(self) -> None:
        """Finalize initialization now that curses has been started."""

        self.commands.register_curses_handlers()

        for control in [x for x in self.items.values() if hasattr(x, "start")]:
            control.start()


# ------------------------------------------------------------------------------

_CONTROLS = None


def Controls() -> _Controls:  # noqa invalid-name
    """Initialize and return controls."""

    global _CONTROLS  # pylint: disable=global-statement
    if not _CONTROLS:
        # _CONTROLS = _Controls("tf2mon.controls", suffix="Control")
        _CONTROLS = _Controls(__package__, suffix="Control")
        _CONTROLS.bind("HelpControl", "F1")
        _CONTROLS.bind("MotdControl", "Ctrl+F1")
        _CONTROLS.bind("DebugFlagControl", "F2")
        _CONTROLS.bind("TauntFlagControl", "F3")
        _CONTROLS.bind("ThroeFlagControl", "Shift+F3")
        _CONTROLS.bind("ShowKDControl", "F4")
        _CONTROLS.bind("ShowKillsControl", "Shift+F4")
        _CONTROLS.bind("UserPanelControl", "F5")
        _CONTROLS.bind("ShowPerksControl", "Shift+F5")
        _CONTROLS.bind("JoinOtherTeamControl", "F6")
        _CONTROLS.bind("SortOrderControl", "F7")
        _CONTROLS.bind("LogLocationControl", "F8")
        _CONTROLS.bind("ResetPaddingControl", "Ctrl+F8")
        _CONTROLS.bind("LogLevelControl", "Shift+F8")
        _CONTROLS.bind("GridLayoutControl", "F9")
        _CONTROLS.bind("ClearChatsControl", "Shift+F9")
        _CONTROLS.bind("ShowDebugControl", "KP_INS")
        _CONTROLS.bind("SingleStepControl", "KP_DEL")
        _CONTROLS.bind("KickLastCheaterControl", "[", game_only=True)
        _CONTROLS.bind("KickLastRacistControl", "]", game_only=True)
        _CONTROLS.bind("KickLastSuspectControl", "\\", game_only=True)
        _CONTROLS.bind("KicksPopControl", "KP_HOME")
        _CONTROLS.bind("KicksClearControl", "KP_LEFTARROW")
        _CONTROLS.bind("KicksPopleftControl", "KP_END")
        _CONTROLS.bind("SpamsPopControl", "KP_PGUP")
        _CONTROLS.bind("SpamsClearControl", "KP_RIGHTARROW")
        _CONTROLS.bind("SpamsPopleftControl", "KP_PGDN")
        _CONTROLS.bind("ClearQueuesControl", "KP_5")
        _CONTROLS.bind("PushControl", "KP_DOWNARROW")

    return _CONTROLS
