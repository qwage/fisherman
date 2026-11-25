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


def test_open_flag_opens_docs_on_localhost(tmp_path, monkeypatch):
    opened = []
    monkeypatch.setattr(cli.uvicorn, "run", lambda *_a, **_kw: None)
    monkeypatch.setattr(cli, "open_when_ready", opened.append)
    monkeypatch.setenv("FISHERMAN_DB", str(tmp_path / "x.db"))

    result = CliRunner().invoke(cli.main, ["run", "--open", "--host", "0.0.0.0"])  # noqa: S104

    assert result.exit_code == 0, result.output
    assert opened == ["http://localhost:8000/docs"]


def test_no_open_flag_opens_nothing(tmp_path, monkeypatch):
    opened = []
    monkeypatch.setattr(cli.uvicorn, "run", lambda *_a, **_kw: None)
    monkeypatch.setattr(cli, "open_when_ready", opened.append)
    monkeypatch.setenv("FISHERMAN_DB", str(tmp_path / "x.db"))

    CliRunner().invoke(cli.main, ["run"])

    assert opened == []


def test_wait_and_open_retries_until_server_answers(monkeypatch):
    attempts = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

    def fake_urlopen(url, timeout):
        attempts.append(url)
        if len(attempts) < 3:
            raise ConnectionRefusedError
        return Response()

    opened = []
    monkeypatch.setattr(cli.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(cli.time, "sleep", lambda _s: None)
    monkeypatch.setattr(cli.webbrowser, "open", opened.append)

    assert cli.wait_and_open("http://localhost:8000/docs") is True
    assert len(attempts) == 3
    assert opened == ["http://localhost:8000/docs"]


def test_wait_and_open_gives_up_after_timeout(monkeypatch):
    opened = []
    monkeypatch.setattr(cli.webbrowser, "open", opened.append)

    assert cli.wait_and_open("http://localhost:1/docs", timeout=0) is False
    assert opened == []
