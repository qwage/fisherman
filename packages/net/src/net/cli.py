"""Command line entry point for the net service: `net run`."""

import os
from pathlib import Path

import click
import uvicorn

from net import paths


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
def run(
    host: str,
    port: int,
    db_path: Path | None,
    log_level: str,
    *,
    reload: bool,
) -> None:
    """Serve the net API."""
    if db_path is not None:
        # The app reads this in its lifespan; reload workers inherit it too.
        os.environ["FISHERMAN_DB"] = str(db_path)
    click.echo(f"Database: {paths.db_path()}")

    uvicorn.run(
        "net.api:app",
        host=host,
        port=port,
        reload=reload,
        # Watch only this package's source, not .venv or the other packages.
        reload_dirs=[str(Path(__file__).parent)] if reload else None,
        log_level=log_level,
    )
