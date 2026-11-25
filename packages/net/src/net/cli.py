"""Command line entry point for the net service: `net run`."""

import os
import time
import urllib.request
import webbrowser
from pathlib import Path

import click
import uvicorn

from net import paths


def open_when_ready(url: str) -> None:
    """Open `url` in a browser once it responds, without blocking the caller.

    The wait happens in a forked child process, so the server can start in the
    foreground while the child polls, opens the page, and exits.
    """
    if os.fork() == 0:
        try:
            wait_and_open(url)
        finally:
            os._exit(0)


def wait_and_open(url: str, timeout: float = 30) -> bool:
    """Poll `url` until it answers, then open it; return whether it opened."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            # Only ever our own http://localhost URL, never user input.
            with urllib.request.urlopen(url, timeout=1):  # noqa: S310
                pass
        except OSError:
            time.sleep(0.2)
        else:
            webbrowser.open(url)
            return True
    return False


@click.group()
def main() -> None:
    """Catch sensor readings from the bobbers and keep them in the pond."""


@main.command("db-path")
def db_path_command() -> None:
    """Print the path to the database file ($FISHERMAN_DB if set)."""
    click.echo(paths.db_path())


@main.command()
@click.option(
    "--host",
    default="127.0.0.1",
    show_default=True,
    envvar="NET_HOST",
    help="Interface to bind; use 0.0.0.0 so bobbers on the LAN can reach it.",
)
@click.option("--port", default=8000, show_default=True, envvar="NET_PORT", type=int)
@click.option(
    "--db",
    "db_path",
    default=None,
    type=click.Path(dir_okay=False, path_type=Path),
    help=(
        "SQLite database file; created along with its directory if missing. "
        f"Defaults to $FISHERMAN_DB, else {paths.data_dir() / paths.DB_FILENAME}."
    ),
)
@click.option(
    "--reload/--no-reload",
    default=False,
    show_default=True,
    help="Restart on code changes (development only).",
)
@click.option(
    "--log-level",
    default="info",
    show_default=True,
    type=click.Choice(["critical", "error", "warning", "info", "debug"]),
)
@click.option(
    "--open",
    "open_browser",
    is_flag=True,
    help="Open the API docs in a browser once the server is up.",
)
def run(
    host: str,
    port: int,
    db_path: Path | None,
    log_level: str,
    *,
    reload: bool,
    open_browser: bool,
) -> None:
    """Serve the net API."""
    if db_path is not None:
        # The app reads this in its lifespan; reload workers inherit it too.
        os.environ["FISHERMAN_DB"] = str(db_path)
    click.echo(f"Database: {paths.db_path()}")

    if open_browser:
        # A browser can't visit 0.0.0.0; the server is on this machine anyway.
        browser_host = "localhost" if host in {"0.0.0.0", "::"} else host  # noqa: S104
        open_when_ready(f"http://{browser_host}:{port}/docs")

    uvicorn.run(
        "net.api:app",
        host=host,
        port=port,
        reload=reload,
        # Watch only this package's source, not .venv or the other packages.
        reload_dirs=[str(Path(__file__).parent)] if reload else None,
        log_level=log_level,
    )
