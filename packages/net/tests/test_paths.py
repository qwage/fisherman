from pathlib import Path

from fastapi.testclient import TestClient

from net import paths
from net.api import app


def test_macos_uses_application_support(monkeypatch):
    monkeypatch.setattr(paths.sys, "platform", "darwin")

    assert paths.data_dir() == (
        Path.home() / "Library" / "Application Support" / "fisherman"
    )


def test_linux_uses_xdg_data_home(monkeypatch, tmp_path):
    monkeypatch.setattr(paths.sys, "platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    assert paths.data_dir() == tmp_path / "fisherman"


def test_linux_falls_back_to_local_share(monkeypatch):
    monkeypatch.setattr(paths.sys, "platform", "linux")
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)

    assert paths.data_dir() == Path.home() / ".local" / "share" / "fisherman"


def test_env_override_wins(monkeypatch, tmp_path):
    monkeypatch.setenv("FISHERMAN_DB", str(tmp_path / "x.db"))

    assert paths.db_path() == tmp_path / "x.db"


def test_app_startup_creates_missing_data_dir(monkeypatch, tmp_path):
    monkeypatch.delenv("FISHERMAN_DB", raising=False)
    monkeypatch.setattr(paths, "data_dir", lambda: tmp_path / "fresh" / "fisherman")

    with TestClient(app):
        pass

    assert (tmp_path / "fresh" / "fisherman" / "fisherman.db").is_file()
