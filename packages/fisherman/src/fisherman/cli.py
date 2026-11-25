"""Command line entry point for the dashboard: `fisherman run`."""

import os
import sys
from pathlib import Path

import click

APP = Path(__file__).with_name("app.py")


@click.group()
def main() -> None:
    """Dashboard for managing hobbyist fishtank systems."""


@main.command()
def run() -> None:
    """Serve the Streamlit dashboard on port 8501."""
    argv = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP),
        # Don't open a browser or prompt for an email on first run.
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]

    os.execv(sys.executable, argv)  # noqa: S606
