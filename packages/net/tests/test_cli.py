import os

from click.testing import CliRunner

from net import cli


def test_run_passes_db_and_starts_uvicorn(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(cli.uvicorn, "run", lambda *a, **kw: calls.append((a, kw)))
    monkeypatch.delenv("FISHERMAN_DB", raising=False)
    db = tmp_path / "data" / "pond.db"

    result = CliRunner().invoke(
        cli.main,
        ["run", "--host", "0.0.0.0", "--port", "9000", "--db", str(db)],  # noqa: S104
    )

    assert result.exit_code == 0, result.output
    assert os.environ["FISHERMAN_DB"] == str(db)
    assert str(db.resolve()) in result.output
    [(args, kwargs)] = calls
    assert args == ("net.api:app",)
    assert kwargs["host"] == "0.0.0.0"  # noqa: S104
    assert kwargs["port"] == 9000
    assert kwargs["reload"] is False
    assert kwargs["reload_dirs"] is None


def test_reload_watches_only_net_source(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(cli.uvicorn, "run", lambda *a, **kw: calls.append(kw))
    monkeypatch.setenv("FISHERMAN_DB", str(tmp_path / "x.db"))

    result = CliRunner().invoke(cli.main, ["run", "--reload"])

    assert result.exit_code == 0, result.output
    [kwargs] = calls
    assert kwargs["reload"] is True
    [watched] = kwargs["reload_dirs"]
    assert watched.endswith("src/net")


def test_db_path_prints_default(tmp_path, monkeypatch):
    monkeypatch.delenv("FISHERMAN_DB", raising=False)
    monkeypatch.setattr(cli.paths, "data_dir", lambda: tmp_path)

    result = CliRunner().invoke(cli.main, ["db-path"])

    assert result.exit_code == 0, result.output
    assert result.output == f"{tmp_path / 'fisherman.db'}\n"


def test_db_path_respects_env(tmp_path, monkeypatch):
    monkeypatch.setenv("FISHERMAN_DB", str(tmp_path / "other.db"))

    result = CliRunner().invoke(cli.main, ["db-path"])

    assert result.output == f"{tmp_path / 'other.db'}\n"


def test_run_defaults_to_app_data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(cli.uvicorn, "run", lambda *_a, **_kw: None)
    monkeypatch.delenv("FISHERMAN_DB", raising=False)
    monkeypatch.setattr(cli.paths, "data_dir", lambda: tmp_path / "appdata")

    result = CliRunner().invoke(cli.main, ["run"])

    assert result.exit_code == 0, result.output
    assert str(tmp_path / "appdata" / "fisherman.db") in result.output
