import pytest
from fastapi.testclient import TestClient

from net.api import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("FISHERMAN_DB", str(tmp_path / "test.db"))
    with TestClient(app) as test_client:  # runs lifespan: opens the pond
        yield test_client


def _post(client, sensor_id, ts, temp_c):
    return client.post(
        "/readings",
        json={"sensor_id": sensor_id, "ts": ts, "temp_c": temp_c},
    )


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_ingest_then_latest(client):
    assert _post(client, "tank1", "2026-01-01T12:00:00+00:00", 25.0).status_code == 201

    [latest] = client.get("/readings/latest").json()

    assert latest["sensor_id"] == "tank1"
    assert latest["temp_c"] == 25.0


def test_readings_filters_by_sensor_and_since(client):
    _post(client, "a", "2026-01-01T12:00:00+00:00", 20.0)
    _post(client, "a", "2026-01-01T12:01:00+00:00", 21.0)
    _post(client, "b", "2026-01-01T12:01:00+00:00", 30.0)

    response = client.get(
        "/readings",
        params={"sensor_id": "a", "since": "2026-01-01T12:00:30+00:00"},
    )

    assert [r["temp_c"] for r in response.json()] == [21.0]


def test_naive_timestamp_is_rejected(client):
    response = _post(client, "tank1", "2026-01-01T12:00:00", 25.0)

    assert response.status_code == 422
