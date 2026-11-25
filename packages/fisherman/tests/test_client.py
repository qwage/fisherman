from datetime import UTC, datetime

import httpx

from fisherman.client import Reading, is_healthy, latest_readings, readings_since


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


def test_is_healthy_true_when_net_answers_ok():
    transport = httpx.MockTransport(
        lambda _request: httpx.Response(200, json={"status": "ok"}),
    )

    assert is_healthy("http://net.test", transport=transport) is True


def test_is_healthy_false_on_error_status():
    transport = httpx.MockTransport(lambda _request: httpx.Response(503))

    assert is_healthy("http://net.test", transport=transport) is False


def test_is_healthy_false_when_net_is_down():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    assert (
        is_healthy("http://net.test", transport=httpx.MockTransport(handler)) is False
    )


def test_readings_since_sends_since_and_limit():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.url)
        return httpx.Response(200, json=[])

    since = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    result = readings_since(
        "http://net.test",
        since,
        limit=50,
        transport=httpx.MockTransport(handler),
    )

    assert result == []
    [url] = seen
    assert url.path == "/readings"
    assert url.params["since"] == "2026-01-01T12:00:00+00:00"
    assert url.params["limit"] == "50"
