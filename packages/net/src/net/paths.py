"""Where net keeps its files on each platform."""

import os
import sys
from pathlib import Path

APP_NAME = "fisherman"
DB_FILENAME = "fisherman.db"


def data_dir() -> Path:
    """Return the per-user data directory for the app.

    - macOS: ``~/Library/Application Support/fisherman``
    - Linux (and anything else): ``$XDG_DATA_HOME/fisherman``, falling back to
      ``~/.local/share/fisherman``
    """
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        xdg = os.environ.get("XDG_DATA_HOME")
        base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    return base / APP_NAME


def db_path() -> Path:
    """Return the database file: ``$FISHERMAN_DB`` if set, else in `data_dir`."""
    override = os.environ.get("FISHERMAN_DB")
    if override:
        return Path(override).expanduser().resolve()
    return data_dir() / DB_FILENAME
