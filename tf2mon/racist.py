"""Racist."""

import re
from pathlib import Path
from typing import Pattern

from loguru import logger

_RE_RACIST: Pattern[str] | None = None


def load_racist_data(path: Path) -> None:
    """Docstring."""

    global _RE_RACIST  # pylint: disable=global-statement

    logger.info(f"Reading `{path}`")
    lines = path.read_text(encoding="utf-8").splitlines()
    _RE_RACIST = re.compile("|".join(lines), flags=re.IGNORECASE) if len(lines) > 0 else None


def is_racist_text(text: str) -> bool:
    """Return True if this user appears to be racist."""

    return _RE_RACIST is not None and _RE_RACIST.search(text) is not None


def clean_username(username: str) -> str:
    """Return `username` cleaned of racism."""

    if _RE_RACIST is not None:
        m = _RE_RACIST.search(username)
        if m is not None:
            return m.string[: m.start()] + str("n" * (m.end() - m.start())) + m.string[m.end() :]
    return username
