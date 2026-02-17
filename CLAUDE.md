# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands

This project uses PDM (Python Dependency Manager) with a Makefile wrapper.

```bash
make build           # Full build: install deps, lint, test, docs, package
make lint            # Run all linters (black, isort, flake8, mypy)
make test            # Run pytest with coverage (min 49% required)
make pytest_debug    # Run pytest with --capture=no to see print output

# Individual linters
make black           # Format code
make isort           # Sort imports
make flake8          # Run flake8
make mypy            # Run mypy (strict mode)

# Run a single test
python -m pytest tests/test_specific.py -v
python -m pytest tests/test_specific.py::test_function -v
```

## Code Style

- Line length: 97 characters (black, isort, pylint)
- Type hints required (mypy strict mode)
- Google-style docstrings
- Class, method, and function docstrings should be followed by 1 blank line (per D202 ignore)

## Architecture

**tf2mon** is an interactive terminal application that monitors Team Fortress 2 games by reading the console log file.

### Core Components

- **`cli.py`** - Entry point (`tf2mon.cli:main`), extends `libcli.BaseCLI`
- **`monitor.py`** - Main coordinator, manages two threads:
  - GAME thread: reads console log via `conlog.py`
  - MAIN thread: handles keyboard/mouse input via `admin.py`
- **`ui.py`** - Curses-based UI built on `libcurses`, manages grid layout and windows
- **`controller.py`** - Registry of all user controls, generates TF2 exec scripts

### Shared State

The `tf2mon/__init__.py` module defines global state accessed throughout the codebase:

- `tf2mon.options` - CLI arguments (set by `cli.py`)
- `tf2mon.conlog` - Console log reader (set in `monitor._run()`)
- `tf2mon.ui` - UI instance (set in `monitor._run()`)
- `tf2mon.users` - Current game's player collection (reset via `tf2mon.reset_game()`)
- `tf2mon.controller` - Singleton with all control instances

Control singletons are also module-level (e.g., `tf2mon.SingleStepControl`, `tf2mon.ChatsControl`).

### Event System

Console log lines are matched against regex patterns in two categories:

- **`game/`** - Game event handlers (kill, suicide, chat, status, connected, lobby, capture, perk)
- **`controls/`** - UI control handlers (kicks, spams, sort order, layout, logging)

Each handler extends `GameEvent` (in `gameevent.py`) or `Control` (in `control.py`).

### Player State

- **`users.py`** - Collection of all players in current game
- **`user.py`** - Individual player with stats (kills, deaths, K/D, opponents)
- **`player.py`** - SQLite database table for persistent player data (cheater/racist/bot flags)
- **`steamweb.py`** - Steam Web API integration for player profiles

### Layout System

- **`layouts/`** - Display layout templates (CHAT, DEFAULT, FULL, TALL, WIDE)
- **`baselayout.py`** - Base class for grid-based window arrangements

## Configuration

Config file: `~/.tf2mon.toml`

```toml
[tf2mon]
tf2_install_dir = "/path/to/TF2/installation"
webapi_key = "your-steam-webapi-key"
player_name = "Your Name"
```

## Dependencies

Key external packages:
- `rlane-libcli` / `rlane-libcurses` - Custom CLI and curses frameworks
- `steam` - Steam Web API
- `loguru` - Logging
- `fuzzywuzzy` - Fuzzy string matching
