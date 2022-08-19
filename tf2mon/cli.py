"""Command line interface."""

import contextlib
import threading
from pathlib import Path
from typing import Optional

import xdg
from libcli import BaseCLI
from loguru import logger

import tf2mon
import tf2mon.controls
import tf2mon.layouts
from tf2mon.conlog import Conlog
from tf2mon.controls import Controls
from tf2mon.database import Database
from tf2mon.hacker import HackerManager
from tf2mon.logger import configure_logger
from tf2mon.monitor import Monitor
from tf2mon.steamweb import SteamWebAPI


class CLI(BaseCLI):
    """Command line interface."""

    _cachedir = xdg.xdg_cache_home() / __package__

    config = {
        # name of config file.
        "config-file": Path.home().joinpath(".tf2mon.toml"),
        #
        # toml [section-name].
        "config-name": "tf2mon",
        #
        # location of game to monitor
        "tf2_install_dir": Path.home().joinpath(
            "SteamLibrary", "steamapps", "common", "Team Fortress 2", "tf"
        ),
        #
        # basename relative to `tf2_install_dir`.
        "con_logfile": Path("console.log"),
        #
        # databases.
        "database": _cachedir / "tf2mon.db",
        "hackers": _cachedir / "hackers.json",
        "exclude-file": Path(__file__).parent / "data" / "exclude.txt",
        "webapi_key": "",
        # this player.
        "player_name": "Bad Dad",
    }

    # Create all controls.
    controls = Controls("tf2mon.controls", suffix="Control")

    # Bind some controls.
    controls.bind("HelpControl", "F1")
    controls.bind("MotdControl", "Ctrl+F1")
    controls.bind("DebugFlagControl", "F2")
    controls.bind("TauntFlagControl", "F3")
    controls.bind("ThroeFlagControl", "Shift+F3")
    controls.bind("ShowKDControl", "F4")
    controls.bind("ShowKillsControl", "Shift+F4")
    controls.bind("UserPanelControl", "F5")
    controls.bind("JoinOtherTeamControl", "F6")
    controls.bind("SortOrderControl", "F7")
    controls.bind("LogLocationControl", "F8")
    controls.bind("LogLevelControl", "Shift+F8")
    controls.bind("ResetPaddingControl", "Ctrl+F8")
    controls.bind("GridLayoutControl", "F9")
    controls.bind("ShowDebugControl", "KP_INS")
    controls.bind("SingleStepControl", "KP_DEL")
    controls.bind("KickLastCheaterControl", "[", game_only=True)
    controls.bind("KickLastRacistControl", "]", game_only=True)
    controls.bind("KickLastSuspectControl", "\\", game_only=True)
    controls.bind("KicksPopControl", "KP_HOME")
    controls.bind("KicksClearControl", "KP_LEFTARROW")
    controls.bind("KicksPopleftControl", "KP_END")
    controls.bind("SpamsPopControl", "KP_PGUP")
    controls.bind("SpamsClearControl", "KP_RIGHTARROW")
    controls.bind("SpamsPopleftControl", "KP_PGDN")
    # controls.bind("PullControl", "KP_UPARROW")
    controls.bind("ClearQueuesControl", "KP_5")
    controls.bind("PushControl", "KP_DOWNARROW")

    # def debug(self, text: str) -> None:
    #     """Override to silence."""
    # for --merge-hackers

    def init_logging(self, verbose: int) -> None:
        """Set logging levels based on `--verbose`."""

        init_logging_called = self.init_logging_called
        super().init_logging(verbose)
        if not init_logging_called:
            configure_logger()

    def init_parser(self) -> None:
        """Initialize argument parser."""

        self.parser = self.ArgumentParser(
            prog=__package__,
            description=self.dedent(
                """
    Team Fortress II (`TF2`) Console Monitor, `%(prog)s`, is an interactive
    terminal application that displays scoreboards and player statistics of
    an active game. `%(prog)s` can also `--rewind` and `--single-step`
    through previous games.

    `%(prog)s` recognizes and tracks abusive players, such as racists and
    `cathook-bots`. It provides application and in-game key-bindings to
    `CALLVOTE KICK` cheaters/hackers, or mark as racist or suspect.

    `%(prog)s` reads TF2's console logfile (`con_logfile`), creates action
    scripts in TF2's `cfg/user` directory, and binds keys for gamer to
    press to take those actions, such as issue `SAY` and `CALLVOTE KICK`
    commands.

    Other in-game key-bindings taunt gamer's last victim/killer with a
    `CHAT` message customized with their name, k/d ratio, rotating spam,
    weapon and duel-scores (`Taunt` and `Throe`).

    By default, `%(prog)s` starts reading `con_logfile` from its end
    (`--no-rewind`), and `--follow`s its tail.
                """
            ),
        )

    def add_arguments(self) -> None:
        """Add arguments to parser."""

        rewind = self.parser.add_mutually_exclusive_group()
        arg = rewind.add_argument(
            "--rewind",
            dest="rewind",
            action="store_true",
            default=False,
            help="start from head of logfile",
        )
        self.add_default_to_help(arg)

        arg = rewind.add_argument(
            "--no-rewind",
            dest="rewind",
            action="store_false",
            help="start from tail of logfile",
        )
        self.add_default_to_help(arg)

        follow = self.parser.add_mutually_exclusive_group()
        arg = follow.add_argument(
            "--follow",
            dest="follow",
            action="store_true",
            default=True,
            help="follow end of logfile forever",
        )
        self.add_default_to_help(arg)

        arg = follow.add_argument(
            "--no-follow",
            dest="follow",
            action="store_false",
            help="exit at end of logfile",
        )
        self.add_default_to_help(arg)

        arg = self.parser.add_argument(
            "--tf2-install-dir",
            metavar="DIR",
            default=Path(self.config["tf2_install_dir"]),
            type=Path,
            help="TF2 installation directory",
        )
        self.add_default_to_help(arg)

        self.controls.add_arguments_to(self.parser)

        arg = self.parser.add_argument(
            "con_logfile",
            default=Path(self.config["con_logfile"]),
            nargs="?",
            type=Path,
            help="TF2 console logfile; relative to `--tf2-install-dir`",
        )
        self.add_default_to_help(arg)

        self.parser.add_argument(
            "--list-con-logfile",
            action="store_true",
            help="show path to logfile and exit",
        )

        self.parser.add_argument(
            "--trunc-con-logfile",
            action="store_true",
            help="truncate logfile and exit",
        )

        self.parser.add_argument(
            "--clean-con-logfile",
            action="store_true",
            help="filter-out excluded lines from logfile to stdout and exit",
        )

        arg = self.parser.add_argument(
            "--exclude-file",
            metavar="FILE",
            default=Path(self.config["exclude-file"]),
            type=Path,
            help="exclude lines that match patterns in `FILE`",
        )
        self.add_default_to_help(arg)

        group = self.parser.add_argument_group("Debugging options")

        group.add_argument(
            "--single-step",
            action="store_true",
            help="single-step at startup",
        )

        group.add_argument(
            "--break",
            dest="breakpoint",
            type=int,
            metavar="LINENO",
            help="single-step at line `LINENO`",
        )

        group.add_argument(
            "--search",
            metavar="PATTERN",
            help="single-step when line matches `PATTERN`; add `/i` to ignore case.",
        )

        group.add_argument(
            "--inject-cmd",
            dest="inject_cmds",
            metavar="LINENO:CMD",
            action="append",
            help="inject `CMD` before line `LINENO`",
        )

        group.add_argument(
            "--inject-file",
            metavar="FILE",
            help="read list of inject commands from `FILE`",
        )

        arg = group.add_argument(
            "--toggles",
            action="store_true",
            help="allow toggles when `--rewind`",
        )
        self.add_default_to_help(arg)

        group = self.parser.add_argument_group("Database options")

        arg = group.add_argument(
            "--database",
            metavar="FILE",
            default=Path(self.config["database"]),
            type=Path,
            help="main database",
        )
        self.add_default_to_help(arg)

        arg = group.add_argument(
            "--hackers",
            metavar="FILE",
            default=Path(self.config["hackers"]),
            type=Path,
            help="hackers database",
        )
        self.add_default_to_help(arg)

        group.add_argument(
            "--print-steamids",
            nargs="+",
            metavar="STEAMID",
            help="print `ISteamUser.GetPlayerSummaries` for `STEAMID` and exit",
        )

        group.add_argument(
            "--print-hackers",
            action="store_true",
            help="print hackers database and exit",
        )

        # group.add_argument(
        #     "--merge-hackers",
        #     metavar="FILE",
        #     type=Path,
        #     help="merge `FILE` with `--hackers FILE` to `stdout` and exit",
        # )

        self.parser.add_argument_group(
            "Configuration file",
            self.dedent(
                """
    The configuration file (see `--config FILE` below) defines local
    settings:

        [%(prog)s]
        tf2_install_dir = "/path/to/your/tf2/installation"
        webapi_key = "your-steamworks-webapi-key"
        player_name = "Your Name"
                """
            ),
        )

        self.parser.add_argument_group(
            "In-Game Controls, Numpad",
            self.dedent(
                """
    While playing TF2, use the `Numpad` to kick cheaters, and generate
    `Taunt` and death-`Throe` spam.

    Messages are placed into queues, and may be popped off either end.

        Queues -->    Kicks     Admin     Spams
                        |         |         |
                        v         v         v
                   +---------+---------+---------+
        last/      |         |         |         |
        newest --> |   pop   |         |   pop   |
                   |         |         |         |
                   +---------+---------+---------+
                   |         |         |         |
                   |  clear  |  clear  |  clear  |
                   |         |  both   |         |
                   +---------+---------+---------+
        first/     |         |         |         |
        oldest --> | popleft |  vet    | popleft |
                   |         |         |         |
                   +---------+---------+---------+

    To vet new players that have joined the game, `%(prog)s` needs their
    `steamid`s, and to get them, gamer must press `NUMPAD-DOWNARROW`. The
    `status` panel will be highlighted when the monitor needs steamids.

    When detected, `%(prog)s` pushes hackers onto the `Kicks` queue, and
    alerts the gamer, who may then press `HOME`/`END` to issue `CHAT`
    and `CALLVOTE KICK` commands.

    When gamer kills an opponent, `%(prog)s` pushes a `Taunt` onto the
    `Spams` queue; on death, a `Throe`. Enable/disable with `F3`. Send
    with `PGUP`/`PGDN`.

    The monitor can only push actions onto the queues; gamer must pop
    for action to be taken, or clear to discard.
                """
            ),
        )

        self.parser.add_argument_group(
            "Duels",
            self.dedent(
                """
    The user-panel displays battles with opponents, grouped by weapon (and
    its state when fired).

        ┌─────────────────────────────────────────────────────────────────────┐
        │Duels:                                                               │
        │ 4 and  2 vs GLaDOS                                                  │
        │             K  2 soldier        quake_rl                            │
        │             K  1 pyro           flamethrower                        │
        │             K  1 pyro     +crit flamethrower         +Low Gravity   │
        │             D  2 heavy          minigun                             │
        │ 5 and  0 vs CreditToTeam                                            │
        │             K  2 soldier        quake_rl                            │
        │             K  2 pyro     +crit flamethrower                        │
        │             K  1 pyro           flamethrower                        │
        │ 3 and  1 vs Aperture Science Prototype XR7                          │
        │             K  1 soldier        world                               │
        │             K  1 soldier        quake_rl             +Invisibility  │
        │             K  1 pyro     +crit flamethrower                        │
        │             D  1 demo           player                              │
        └─────────────────────────────────────────────────────────────────────┘
                """
            ),
        )

        self.parser.add_argument_group(
            "Function Keys",
            "These function keys are available in-game and in the monitor:\n\n"
            + self.controls.fkey_help(),
        )

        self.parser.add_argument_group(
            "Where to Operate",
            self.dedent(
                """
    `%(prog)s` works by reading the `con_logfile` to which `TF2` logs
    messages during the game. `%(prog)s` can either "tail -f" an active
    game, or `--rewind` and replay saved logfiles. Press `Enter` in the
    admin console to process the next line when in `--single-step` mode.
    Type `quit` or press `^D` to exit.

        `One-machine, Two-monitors`
            Run `%(prog)s` on a secondary monitor, while playing game on
            primary monitor.

        `Two-machines, SSH`
            ssh from another machine and run.

        `Two-machines, NFS`
            cross-mount TF2's `cfg` tree to another box and run from there.
                """
            ),
        )

        self.parser.add_argument_group(
            "Terminal Size",
            self.dedent(
                """
    `%(prog)s` requires a large terminal. Maximize the window, and use keys
    (maybe `Ctrl-Minus` and `Shift-Ctrl-Plus`) to resize. The wider the
    terminal, the more player data will be displayed:

        36x146 minimum
        42x173 display personaname
        52x211 display realname
        62x272 display age/location
                """
            ),
        )

        self.parser.add_argument_group(
            "Resizable Windows",
            self.dedent(
                """
    `Drag-and-drop` an interior border to resize the windows on either side.

    `Double-click` an interior border to enter `Resize Mode`.
        `scroll-wheel` and `arrows` move the border.
        `click`, `enter` or `esc` to exit.
                """
            ),
        )

        self.parser.add_argument_group(
            "Scoreboard",
            self.dedent(
                """
    `Single-click` user to highlight and follow.
    `Double-click` user to kick as cheater.
    `Triple-click` user to kick as racist.
    `F7` to change sort column.
                """
            ),
        )

    def main(self) -> None:
        """Command line interface entry point (method)."""

        tf2mon.config = self.config
        tf2mon.options = self.options

        if self.options.con_logfile == self.config["con_logfile"]:
            # Not given on command line; prefix with effective parent.
            # (configured default is a basename relative to `tf2_install_dir`)
            self.options.con_logfile = Path(
                self.config["tf2_install_dir"],
                self.config["con_logfile"],
            )

        if self.options.single_step and not self.options.follow:
            self.parser.error("--no-follow not allowed with --single-step")

        if self.options.list_con_logfile:
            print(self.options.con_logfile)
            self.parser.exit()

        if self.options.trunc_con_logfile:
            Conlog(self.options.con_logfile).trunc()
            logger.info(f"con_logfile {str(self.options.con_logfile)!r} truncated; Exiting.")
            self.parser.exit()

        if self.options.clean_con_logfile:
            Conlog(self.options.con_logfile, exclude_file=self.options.exclude_file).clean()
            logger.info(f"con_logfile {str(self.options.con_logfile)!r} cleaned; Exiting.")
            self.parser.exit()

        if self.options.print_steamids:
            Database(self.options.database)
            api = SteamWebAPI(webapi_key=self.config.get("webapi_key"))
            for steamid in self.options.print_steamids:
                print(api.fetch_steamid(steamid))
            self.parser.exit()

        if self.options.print_hackers:
            Database(self.options.database)
            hackers = HackerManager(self.options.hackers)
            with contextlib.suppress(BrokenPipeError):
                hackers.print_report()
            self.parser.exit()

        # if self.options.merge_hackers:
        #     hackers = HackerManager(self.options.hackers)
        #     hackers.load(self.options.merge_hackers)
        #     print(str(hackers))
        #     self.parser.exit()

        tf2mon.monitor = Monitor(self)
        tf2mon.monitor.run()


def main(args: Optional[list[str]] = None) -> None:
    """Command line interface entry point (function)."""

    threading.current_thread().name = "MAIN"
    return CLI(args).main()
