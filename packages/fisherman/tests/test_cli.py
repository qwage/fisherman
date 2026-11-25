from click.testing import CliRunner

from fisherman import cli


def test_run_execs_streamlit_headless(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.os, "execv", lambda path, argv: calls.append(argv))

    result = CliRunner().invoke(cli.main, ["run"])

    assert result.exit_code == 0, result.output
    [argv] = calls
    assert argv[1:5] == ["-m", "streamlit", "run", str(cli.APP)]
    assert argv[argv.index("--server.headless") + 1] == "true"


def test_app_file_ships_with_package():
    assert cli.APP.is_file()


def test_open_flag_opens_dashboard_before_exec(monkeypatch):
    events = []
    monkeypatch.setattr(cli, "open_when_ready", events.append)
    monkeypatch.setattr(cli.os, "execv", lambda *_a: events.append("exec"))

    result = CliRunner().invoke(cli.main, ["run", "--open"])

    assert result.exit_code == 0, result.output
    assert events == ["http://localhost:8501", "exec"]


def test_open_flag_keeps_streamlit_headless(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "open_when_ready", lambda _url: None)
    monkeypatch.setattr(cli.os, "execv", lambda _path, argv: calls.append(argv))

    CliRunner().invoke(cli.main, ["run", "--open"])

    [argv] = calls
    assert argv[argv.index("--server.headless") + 1] == "true"
