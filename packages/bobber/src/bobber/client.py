"""Client that reports sensor readings to the net service."""

from datetime import datetime

import httpx


def send_reading(base_url: str, sensor_id: str, ts: datetime, temp_c: float) -> None:
    """Send one reading to the net service, raising on any HTTP error."""
    response = httpx.post(
        f"{base_url}/readings",
        json={"sensor_id": sensor_id, "ts": ts.isoformat(), "temp_c": temp_c},
        timeout=10,
    )
    response.raise_for_status()
