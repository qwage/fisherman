from datetime import UTC, datetime, timedelta, timezone

import pytest
from sqlalchemy.orm import Session

from net.pond import db
from net.pond.models import ReadingPayload

T0 = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


@pytest.fixture
def session(tmp_path):
    engine = db.open_engine(tmp_path / "test.db")
    with Session(engine) as test_session:
        yield test_session
    engine.dispose()


def test_insert_and_latest_roundtrip(session):
    older = ReadingPayload(sensor_id="tank1", ts=T0, temp_c=24.0)
    newer = ReadingPayload(sensor_id="tank1", ts=T0 + timedelta(minutes=1), temp_c=25.5)

    db.insert_reading(session, older)
    db.insert_reading(session, newer)
    db.insert_reading(session, newer)  # duplicate is ignored

    [latest] = db.latest_readings(session)
    assert (latest.sensor_id, latest.ts, latest.temp_c) == (
        newer.sensor_id,
        newer.ts,
        newer.temp_c,
    )


def test_non_utc_offsets_are_stored_as_utc(session):
    # 14:00+05:00 is 09:00 UTC, so it is *older* than T0 (12:00 UTC) even
    # though its wall-clock time is later. A plain DateTime column on SQLite
    # drops the offset and would pick it as the latest.
    plus5 = timezone(timedelta(hours=5))
    early = datetime(2026, 1, 1, 14, 0, tzinfo=plus5)
    db.insert_reading(session, ReadingPayload(sensor_id="a", ts=early, temp_c=20.0))
    db.insert_reading(session, ReadingPayload(sensor_id="a", ts=T0, temp_c=21.0))

    [latest] = db.latest_readings(session)

    assert latest.temp_c == 21.0
    assert latest.ts == T0
    assert latest.ts.tzinfo is UTC


def test_latest_is_per_sensor(session):
    db.insert_reading(session, ReadingPayload(sensor_id="a", ts=T0, temp_c=20.0))
    db.insert_reading(session, ReadingPayload(sensor_id="b", ts=T0, temp_c=30.0))

    assert {r.sensor_id: r.temp_c for r in db.latest_readings(session)} == {
        "a": 20.0,
        "b": 30.0,
    }


def test_recent_readings_filters_and_orders(session):
    for minute in range(3):
        ts = T0 + timedelta(minutes=minute)
        db.insert_reading(
            session,
            ReadingPayload(sensor_id="a", ts=ts, temp_c=20.0 + minute),
        )
    db.insert_reading(session, ReadingPayload(sensor_id="b", ts=T0, temp_c=30.0))

    since = T0 + timedelta(minutes=1)
    result = db.recent_readings(session, sensor_id="a", since=since)

    assert [r.temp_c for r in result] == [22.0, 21.0]  # newest first, only sensor a
