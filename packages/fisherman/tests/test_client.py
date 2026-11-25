from datetime import UTC, datetime

import httpx

from fisherman.client import Reading, latest_readings


def test_latest_readings_parses_response():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/readings/latest"
        return httpx.Response(
            200,
            json=[
                {
                    "sensor_id": "tank1",
                    "ts": "2026-01-01T12:00:00Z",
                    "temp_c": 25.0,
                },
            ],
        )

    result = latest_readings(
        "http://net.test",
        transport=httpx.MockTransport(handler),
    )

    assert result == [
        Reading("tank1", datetime(2026, 1, 1, 12, 0, tzinfo=UTC), 25.0),
    ]
