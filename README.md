### tf2mon - Team Fortress 2 Console Monitor

#### Usage
    tf2mon [--tf2-install-dir DIR] [--rewind | --no-rewind]
           [--follow | --no-follow] [--list-con-logfile]
           [--trunc-con-logfile] [--clean-con-logfile]
           [--exclude-file FILE] [--layout {CHAT,DFLT,FULL,TALL,MRGD,WIDE}]
           [--log-location {MOD,NAM,THM,THN,FILE,NUL}]
           [--sort-order {AGE,STEAMID,CONN,K,KD,USERNAME}] [--single-step]
           [--break LINENO] [--search PATTERN] [--inject-cmd LINENO:CMD]
           [--inject-file FILE] [--toggles] [--database FILE]
           [--hackers FILE] [--print-steamids STEAMID [STEAMID ...]]
           [--print-hackers] [-h] [-v] [-V] [--config FILE]
           [--print-config] [--print-url] [--completion [SHELL]]
           [con_logfile]
    
Team Fortress II (`TF2`) Console Monitor, `tf2mon`, is an interactive
terminal application that displays scoreboards and player statistics of
an active game. `tf2mon` can also `--rewind` and `--single-step`
through previous games.

`tf2mon` recognizes and tracks abusive players, such as racists and
`cathook-bots`. It provides application and in-game key-bindings to
`CALLVOTE KICK` cheaters/hackers, or mark as racist or suspect.

`tf2mon` reads TF2's console logfile (`con_logfile`), creates action
scripts in TF2's `cfg/user` directory, and binds keys for gamer to
press to take those actions, such as issue `SAY` and `CALLVOTE KICK`
commands.

Other in-game key-bindings taunt gamer's last victim/killer with a
`CHAT` message customized with their name, k/d ratio, rotating spam,
weapon and duel-scores (`Taunt` and `Throe`).

By default, `tf2mon` starts reading `con_logfile` from its end
(`--no-rewind`), and `--follow`s its tail.

#### Positional Arguments
    con_logfile         TF2 console logfile; relative to `--tf2-install-dir`
                        (default: `console.log`).

#### Options
    --tf2-install-dir DIR
                        TF2 installation directory (default: `~/tf2`).
    --rewind            Start from head of logfile (default: `False`).
    --no-rewind         Start from tail of logfile (default: `True`).
    --follow            Follow end of logfile forever (default: `True`).
    --no-follow         Exit at end of logfile (default: `False`).
    --list-con-logfile  Show path to logfile and exit.
    --trunc-con-logfile
                        Truncate logfile and exit.
    --clean-con-logfile
                        Filter-out excluded lines from logfile to stdout and
                        exit.
    --exclude-file FILE
                        Exclude lines that match patterns in `FILE` (default:
                        `~/dev/tf2mon/tf2mon/data/exclude.txt`).
    --layout {CHAT,DFLT,FULL,TALL,MRGD,WIDE}
                        Choose display layout (fkey: `F9`) (default: `MRGD`).
    --log-location {MOD,NAM,THM,THN,FILE,NUL}
                        Choose format of logger location field (fkey: `F8`)
                        (default: `NUL`).
    --sort-order {AGE,STEAMID,CONN,K,KD,USERNAME}
                        Choose sort order (fkey: `F7`) (default: `KD`).

#### Debugging options
    --single-step       Single-step at startup.
    --break LINENO      Single-step at line `LINENO`.
    --search PATTERN    Single-step when line matches `PATTERN`; add `/i` to
                        ignore case.
    --inject-cmd LINENO:CMD
                        Inject `CMD` before line `LINENO`.
    --inject-file FILE  Read list of inject commands from `FILE`.
    --toggles           Allow toggles when `--rewind` (default: `False`).

#### Database options
    --database FILE     Main database (default: `~/.cache/tf2mon/tf2mon.db`).
    --hackers FILE      Hackers database (default:
                        `~/.cache/tf2mon/hackers.json`).
    --print-steamids STEAMID [STEAMID ...]
                        Print `ISteamUser.GetPlayerSummaries` for `STEAMID`
                        and exit.
    --print-hackers     Print hackers database and exit.

#### Configuration file
  The configuration file (see `--config FILE` below) defines local
  settings:
  
      [tf2mon]
      tf2_install_dir = "/path/to/your/tf2/installation"
      webapi_key = "your-steamworks-webapi-key"
      player_name = "Your Name"

#### Function Keys
  These function keys are available in-game and in the monitor:
  
                 F1 Display Help.
            ctrl+F1 Display Message of the Day.
           shift+F1 Display file.
                 F2 Enable/disable debug (use `ECHO` or `SAY`).
                 F3 Enable/disable `Taunt` messages.
           shift+F3 Enable/disable `Throe` messages.
                 F4 Include `Kill/Death ratio` in `User.moniker`.
           shift+F4 Display kills in journal window.
                 F5 Cycle contents of User Panel.
           shift+F5 Display perks in journal window.
                 F6 Join Other Team.
                 F7 Cycle scoreboard Sort column.
                 F8 Cycle logger `location` format.
            ctrl+F8 Reset logger `padding`.
           shift+F8 Cycle logger `level`.
                 F9 Cycle grid layout.
            ctrl+F9 Refresh chat window(s).
           shift+F9 Clear chat window(s).
             KP_INS Show debugging.
             KP_DEL Start single-stepping.
                  [ Kick last killer as `cheater`.
                  ] Kick last killer as `racist`.
                  \ Mark last killer as `suspect`.
            KP_HOME Pop last/latest kicks queue message.
       KP_LEFTARROW Clear kicks queue.
             KP_END Pop first/oldest kicks queue message.
            KP_PGUP Pop last/latest spams queue message.
      KP_RIGHTARROW Clear spams queue.
            KP_PGDN Pop first/oldest spams queue message.
               KP_5 Clear kicks and spams queues.
       KP_DOWNARROW Push `steamids` from game to monitor.

#### In-Game Controls, Numpad
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
  
  To vet new players that have joined the game, `tf2mon` needs their
  `steamid`s, and to get them, gamer must press `NUMPAD-DOWNARROW`. The
  `status` panel will be highlighted when the monitor needs steamids.
  
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

#### Where to Operate
  `tf2mon` works by reading the `con_logfile` to which `TF2` logs
  messages during the game. `tf2mon` can either "tail -f" an active
  game, or `--rewind` and replay saved logfiles. Press `Enter` in the
  admin console to process the next line when in `--single-step` mode.
  Type `quit` or press `^D` to exit.
  
      `One-machine, Two-monitors`
          Run `tf2mon` on a secondary monitor, while playing game on
          primary monitor.
  
      `Two-machines, SSH`
          ssh from another machine and run.
  
      `Two-machines, NFS`
          cross-mount TF2's `cfg` tree to another box and run from there.

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

#### Log Files
  `tf2mon` writes plaintext messages to `fileno(2)`, and
  colorized messages to `fileno(3)`, when open to a regular file.
  
      $ tf2mon 2>x 3>y

#### General options
    -h, --help          Show this help message and exit.
    -v, --verbose       `-v` for detailed output and `-vv` for more detailed.
    -V, --version       Print version number and exit.
    --config FILE       Use config `FILE` (default: `~/.tf2mon.toml`).
    --print-config      Print effective config and exit.
    --print-url         Print project url and exit.
    --completion [SHELL]
                        Print completion scripts for `SHELL` and exit
                        (default: `bash`).
