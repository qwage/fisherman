"""Client for reading sensor data from the net service."""

from dataclasses import dataclass
from datetime import datetime

import httpx


@dataclass(frozen=True)
class Reading:
    """A temperature reading reported by net."""

    sensor_id: str
    ts: datetime
    temp_c: float


def latest_readings(
    base_url: str,
    *,
    transport: httpx.BaseTransport | None = None,
) -> list[Reading]:
    """Fetch the most recent reading for each sensor from net."""
    with httpx.Client(base_url=base_url, transport=transport, timeout=10) as http:
        response = http.get("/readings/latest")
        response.raise_for_status()
    return [
        Reading(
            sensor_id=item["sensor_id"],
            ts=datetime.fromisoformat(item["ts"]),
            temp_c=item["temp_c"],
        )
        for item in response.json()
    ]
