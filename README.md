### tf2mon - Team Fortress 2 Console Monitor

#### Usage
    tf2mon [--rewind | --no-rewind] [--follow | --no-follow]
           [--tf2-install-dir DIR] [--list-con-logfile]
           [--trunc-con-logfile] [--clean-con-logfile] [--single-step]
           [--break LINENO] [--search PATTERN] [--inject-cmd LINENO:CMD]
           [--inject-file FILE] [--players FILE] [--hackers-base FILE]
           [--hackers-local FILE] [--print-steamid STEAMID] [-h] [-v] [-V]
           [--config FILE] [--print-config] [--print-url]
           [con_logfile]
    
Team Fortress II (`TF2`) Console Monitor (`tf2mon`) is an interactive
terminal application that displays real-time game state and player
statistics of an actively running TF2 game.

`tf2mon` recognizes and tracks `cathook-bots`, and provides both
application and in-game key-bindings to quickly `CALLVOTE KICK`
hackers, mark players as racist, suspect, etc.

`tf2mon` reads TF2's console logfile (`con_logfile`), creates action
scripts in TF2's `cfg` directory, and binds keys for the gamer to press
in-game to take those actions; such as issue `SAY` and `CALLVOTE KICK`
commands.

Other in-game key-bindings taunt gamer's last victim/killer with a
`CHAT` message customized with their name, k/d ratio, weapon and duel-
score (`Taunt` and `Throe`).

By default, `tf2mon` starts reading the con_logfile from its end
(`--no-rewind`), and continues to `--follow` it until interrupted.

#### Positional Arguments
    con_logfile         TF2 console logfile; relative to `--tf2-install-dir`
                        (default: `console.log`).

#### Options
    --rewind            Start from head of logfile (default: `False`).
    --no-rewind         Start from tail of logfile (default: `True`).
    --follow            Follow end of logfile forever (default: `True`).
    --no-follow         Exit at end of logfile (default: `False`).
    --tf2-install-dir DIR
                        TF2 installation directory (default: `~/tf2`).
    --list-con-logfile  Show path to logfile and exit.
    --trunc-con-logfile
                        Truncate logfile and exit.
    --clean-con-logfile
                        Filter-out excluded lines from logfile to stdout and
                        exit.

#### Debugging options
    --single-step       Single-step at startup.
    --break LINENO      Single-step at line `LINENO`.
    --search PATTERN    Single-step when line matches `PATTERN`; add `/i` to
                        ignore case.
    --inject-cmd LINENO:CMD
                        Inject `CMD` before line `LINENO`.
    --inject-file FILE  Read list of inject commands from `FILE`.

#### Database options
    --players FILE      Cache `steam` user data (default:
                        `~/.cache/tf2mon/steamplayers.db`).
    --hackers-base FILE
                        Upstream hackers database (default:
                        `~/.cache/tf2mon/playerlist.milenko-list.json`).
    --hackers-local FILE
                        Local hackers database (default:
                        `~/.cache/tf2mon/playerlist.tf2mon-list.json`).
    --print-steamid STEAMID
                        Print `ISteamUser.GetPlayerSummaries` for `STEAMID`
                        and exit.

#### Configuration file
  The configuration file (see `--config FILE` below) defines local
  settings:
  
      [tf2mon]
      tf2_install_dir = "/path/to/your/tf2/installation"
      webapi_key = "your-steamworks-webapi-key"
      player_name = "Your Name"

#### In-Game Controls, Numpad
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
  
  When detected, `tf2mon` pushes hackers onto the `Kicks` queue, and
  alerts the gamer, who may then press `HOME`/`END` to issue `CHAT`
  and `CALLVOTE KICK` commands.
  
  When gamer kills an opponent, `tf2mon` pushes a `Taunt` onto the
  `Spams` queue; on death, a `Throe`. Enable/disable with `F3`. Send
  with `PGUP`/`PGDN`.
  
  The monitor can only push actions onto the queues; gamer must pop
  for action to be taken, or clear to discard.

#### Duels
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

#### Function Keys
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
      \  Mark last killer as suspect.
      KP_DEL Begin single-stepping.

#### Where to Operate
  `tf2mon` works by reading the `con_logfile` to which `TF2` logs
  messages during the game. `tf2mon` can either "tail -f" an active
  game, or `--rewind` and replay saved logfiles. Press `Enter` in the
  admin console to process the next line when in `--single-step` mode.
  Type `quit` or press `^D` to exit.
  
      `Duel monitors`
          Run `tf2mon` on a secondary monitor, while playing the game on
          the primary monitor. Best performance, but a pain to `Alt-Tab`
          between monitor and game.
  
      `Duel machines, ssh`
          ssh from another machine and run.
  
      `Duel machines, nfs`
          cross-mount TF2's directory to another box and run from there.

#### Terminal Size
  `tf2mon` requires a large terminal. Maximize the window, and use keys
  (maybe `Ctrl-Minus` and `Shift-Ctrl-Plus`) to resize. The wider the
  terminal, the more player data will be displayed:
  
      36x146 minimum
      42x173 display personaname
      52x211 display realname
      62x272 display age/location

#### Resizable Windows
  `Drag-and-drop` an interior border to resize the windows on either side.
  
  `Double-click` an interior border to enter `Resize Mode`.
      `scroll-wheel` and `arrows` move the border.
      `click`, `enter` or `esc` to exit.

#### Scoreboard
  `Single-click` user to highlight and follow.
  `Double-click` user to kick as cheater.
  `Triple-click` user to kick as racist.
  `F7` to change sort column.

#### General options
    -h, --help          Show this help message and exit.
    -v, --verbose       `-v` for detailed output and `-vv` for more detailed.
    -V, --version       Print version number and exit.
    --config FILE       Use config `FILE` (default: `~/.tf2mon.toml`).
    --print-config      Print effective config and exit.
    --print-url         Print project url and exit.
