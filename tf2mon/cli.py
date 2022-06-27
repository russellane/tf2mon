"""Command line interface."""

import threading
from pathlib import Path
from typing import List, Optional

import steam.steamid
import xdg
from libcli import BaseCLI
from loguru import logger

import tf2mon.layouts
from tf2mon.conlog import Conlog
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
        "players": _cachedir / "steamplayers.db",
        "hackers-base": _cachedir / "playerlist.milenko-list.json",
        "hackers-local": _cachedir / "playerlist.tf2mon-list.json",
        "webapi_key": "",
        # this player.
        "player_name": "Bad Dad",
    }

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
    Team Fortress II (`TF2`) Console Monitor (`%(prog)s`) is an interactive
    terminal application that displays real-time game state and player
    statistics of an actively running TF2 game.

    `%(prog)s` recognizes and tracks `cathook-bots`, and provides both
    application and in-game key-bindings to quickly `CALLVOTE KICK`
    hackers, mark players as racist, suspect, etc.

    `%(prog)s` reads TF2's console logfile (`con_logfile`), creates action
    scripts in TF2's `cfg` directory, and binds keys for the gamer to press
    in-game to take those actions; such as issue `SAY` and `CALLVOTE KICK`
    commands.

    Other in-game key-bindings taunt gamer's last victim/killer with a
    `CHAT` message customized with their name, k/d ratio, weapon and duel-
    score (`Taunt` and `Throe`).

    By default, `%(prog)s` starts reading the con_logfile from its end
    (`--no-rewind`), and continues to `--follow` it until interrupted.
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

        arg = self.parser.add_argument(
            "--layout",
            choices=[x.name for x in list(tf2mon.layouts.LAYOUT_ENUM)],
            default=list(tf2mon.layouts.LAYOUT_ENUM)[0].name,
            help="choose display layout",
        )
        self.add_default_to_help(arg)

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
            "--players",
            metavar="FILE",
            default=Path(self.config["players"]),
            type=Path,
            help="cache `steam` user data" "",
        )
        self.add_default_to_help(arg)

        arg = group.add_argument(
            "--hackers-base",
            metavar="FILE",
            default=Path(self.config["hackers-base"]),
            type=Path,
            help="upstream hackers database",
        )
        self.add_default_to_help(arg)

        arg = group.add_argument(
            "--hackers-local",
            metavar="FILE",
            default=Path(self.config["hackers-local"]),
            type=Path,
            help="local hackers database",
        )
        self.add_default_to_help(arg)

        group.add_argument(
            "--print-steamid",
            metavar="STEAMID",
            help="print `ISteamUser.GetPlayerSummaries` for `STEAMID` and exit" "",
        )

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
                   +-----------------------------+
        last/      |         |         |         |
        newest --> |   pop   |  pull   |   pop   |
                   |         |         |         |
                   |---------+---------+---------|
                   |         |         |         |
                   |  clear  |  clear  |  clear  |
                   |         |  both   |         |
                   |---------+---------+---------|
        first/     |         |         |         |
        oldest --> | popleft |  push   | popleft |
                   |         |         |         |
                   +-----------------------------+

    To vet new players that have joined the game, and to remove inactive
    players, press `NUMPAD-DOWNARROW`. The monitor indicates when new
    players have arrived and that key should be pressed; or press it each
    time you die.

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
            self.dedent(
                """
    These function keys are available in-game and in the monitor:

        F1 Display help.
        F2 Toggle Debug (control `say` vs `echo`).
        F3 Enable/disable Taunts and Throes.
        F4 Include kd-ratio in messages.
        F5 Control User-panel display: Kicks, Spams, Duels and Auto.
        F6 Join other team.
        F7 Change scoreboard sort column.
        F8 Change logger location format.
        F9 Change grid layout.
        [  Kick last killer as cheater.
        ]  Kick last killer as racist.
        \\  Mark last killer as suspect.
        KP_DEL Begin single-stepping.
                """
            ),
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

        # if "webapi_key" not in self.config:
        #     self.parser.error("Missing config `webapi_key`")

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
            Conlog(self.options.con_logfile).clean()
            logger.info(f"con_logfile {str(self.options.con_logfile)!r} cleaned; Exiting.")
            self.parser.exit()

        if self.options.print_steamid:
            api = SteamWebAPI(
                dbpath=self.options.players,
                webapi_key=self.config.get("webapi_key"),
            )
            api.connect()
            steamid = steam.steamid.SteamID(self.options.print_steamid)
            if not steamid.is_valid():
                self.parser.error(f"invalid steamid `{self.options.print_steamid}`")
            steam_player = api.find_steamid(steamid)
            print(steam_player)
            self.parser.exit()

        if self.options.layout:  # get enum from name
            self.options.layout = tf2mon.layouts.LAYOUT_ENUM.__dict__[self.options.layout]

        monitor = Monitor(self)
        monitor.run()


def main(args: Optional[List[str]] = None) -> None:
    """Command line interface entry point (function)."""

    threading.current_thread().name = "MAIN"
    return CLI(args).main()
