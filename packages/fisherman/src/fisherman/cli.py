"""Command line entry point for the dashboard: `fisherman run`."""

import os
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

import click

APP = Path(__file__).with_name("app.py")
URL = "http://localhost:8501"


def open_when_ready(url: str) -> None:
    """Open `url` in a browser once it responds, without blocking the caller.

    The wait happens in a forked child process because `run` replaces this
    process with Streamlit; the child polls, opens the page, and exits.
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
    """Dashboard for managing hobbyist fishtank systems."""


@main.command()
@click.option(
    "--open",
    "open_browser",
    is_flag=True,
    help="Open the dashboard in a browser once it is up.",
)
def run(*, open_browser: bool) -> None:
    """Serve the Streamlit dashboard on port 8501."""
    argv = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP),
        # Don't let Streamlit open a browser or prompt for an email on first
        # run (that prompt would hang a service); --open handles the browser.
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    if open_browser:
        open_when_ready(URL)

    os.execv(sys.executable, argv)  # noqa: S606
