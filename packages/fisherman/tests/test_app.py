from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from fisherman import client
from fisherman.client import Reading

APP = str(Path(client.__file__).with_name("app.py"))
NOW = datetime.now(UTC)
READINGS = [
    Reading("tank1", NOW - timedelta(minutes=10), 25.0),
    Reading("tank1", NOW, 25.5),
    Reading("tank2", NOW, 23.0),
]


@pytest.fixture(autouse=True)
def _fresh_cache():
    st.cache_data.clear()  # cached loads would otherwise leak between tests


def _badge(at):
    return at.markdown[0].value


def _stub_net(monkeypatch, *, healthy=True, readings=READINGS):
    monkeypatch.setattr(client, "is_healthy", lambda _url: healthy)
    monkeypatch.setattr(
        client,
        "latest_readings",
        lambda _url: [r for r in readings if r.ts == NOW],
    )
    monkeypatch.setattr(client, "readings_since", lambda _url, _since: readings)


def test_dashboard_shows_health_table_and_chart(monkeypatch):
    _stub_net(monkeypatch)

    at = AppTest.from_file(APP).run()

    assert not at.exception
    assert "net is up" in _badge(at)
    table = at.dataframe[0].value
    assert list(table["sensor_id"]) == ["tank1", "tank2"]
    assert len(at.get("plotly_chart")) == 1


def test_dashboard_reports_net_down(monkeypatch):
    def refuse(_url):
        raise httpx.ConnectError("refused")

    _stub_net(monkeypatch, healthy=False)
    monkeypatch.setattr(client, "latest_readings", refuse)

    at = AppTest.from_file(APP).run()

    assert not at.exception
    assert "unreachable" in _badge(at)
    assert at.error[0].value.startswith("Could not load readings")
    assert len(at.get("plotly_chart")) == 0


def test_dashboard_with_no_readings_shows_hint(monkeypatch):
    _stub_net(monkeypatch, readings=[])

    at = AppTest.from_file(APP).run()

    assert not at.exception
    assert "seed the database" in at.info[0].value
