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
