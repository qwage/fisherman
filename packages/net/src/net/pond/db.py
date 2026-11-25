"""SQLite storage for sensor readings, built on SQLAlchemy."""

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from sqlalchemy import Engine, and_, create_engine, event, func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from net.pond.models import Base, Reading, ReadingPayload


def open_engine(path: str | Path) -> Engine:
    """Create an engine for the SQLite file, enable WAL mode, and create tables."""
    engine = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},  # FastAPI uses a threadpool
    )

    @event.listens_for(engine, "connect")
    def _enable_wal(dbapi_connection, _connection_record) -> None:
        dbapi_connection.execute("PRAGMA journal_mode=WAL")

    Base.metadata.create_all(engine)
    return engine


def insert_reading(session: Session, reading: ReadingPayload) -> None:
    """Store a reading; a repeat of the same (sensor_id, ts) is ignored."""
    statement = (
        sqlite_insert(Reading).values(**reading.model_dump()).on_conflict_do_nothing()
    )
    session.execute(statement)
    session.commit()


def latest_readings(session: Session) -> Sequence[Reading]:
    """Return the most recent reading for each sensor."""
    newest = (
        select(Reading.sensor_id, func.max(Reading.ts).label("ts"))
        .group_by(Reading.sensor_id)
        .subquery()
    )
    statement = select(Reading).join(
        newest,
        and_(Reading.sensor_id == newest.c.sensor_id, Reading.ts == newest.c.ts),
    )
    return session.scalars(statement).all()


def recent_readings(
    session: Session,
    sensor_id: str | None = None,
    since: datetime | None = None,
    limit: int = 1000,
) -> Sequence[Reading]:
    """Return readings newest-first, optionally filtered by sensor and start time."""
    statement = select(Reading).order_by(Reading.ts.desc()).limit(limit)
    if sensor_id is not None:
        statement = statement.where(Reading.sensor_id == sensor_id)
    if since is not None:
        statement = statement.where(Reading.ts >= since)
    return session.scalars(statement).all()
