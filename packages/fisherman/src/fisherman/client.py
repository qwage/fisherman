"""Client for reading sensor data from the net service."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx


@dataclass(frozen=True)
class Reading:
    """A temperature reading reported by net."""

    sensor_id: str
    ts: datetime
    temp_c: float


def is_healthy(
    base_url: str,
    *,
    transport: httpx.BaseTransport | None = None,
) -> bool:
    """Return whether net answers its health check; never raises."""
    try:
        with httpx.Client(base_url=base_url, transport=transport, timeout=2) as http:
            response = http.get("/health")
    except httpx.HTTPError:
        return False
    return response.is_success and response.json().get("status") == "ok"


def latest_readings(
    base_url: str,
    *,
    transport: httpx.BaseTransport | None = None,
) -> list[Reading]:
    """Fetch the most recent reading for each sensor from net."""
    return _get_readings(base_url, "/readings/latest", {}, transport)


def readings_since(
    base_url: str,
    since: datetime,
    *,
    limit: int = 10_000,
    transport: httpx.BaseTransport | None = None,
) -> list[Reading]:
    """Fetch readings for every sensor taken at or after `since`, newest first."""
    params = {"since": since.isoformat(), "limit": limit}
    return _get_readings(base_url, "/readings", params, transport)


def _get_readings(
    base_url: str,
    path: str,
    params: dict[str, Any],
    transport: httpx.BaseTransport | None,
) -> list[Reading]:
    """GET a list of readings from net, raising on any HTTP error."""
    with httpx.Client(base_url=base_url, transport=transport, timeout=10) as http:
        response = http.get(path, params=params)
        response.raise_for_status()
    return [
        Reading(
            sensor_id=item["sensor_id"],
            ts=datetime.fromisoformat(item["ts"]),
            temp_c=item["temp_c"],
        )
        for item in response.json()
    ]
