"""Data models for the pond, where all sensor readings are stored."""

from datetime import UTC, datetime
from typing import override

from pydantic import AwareDatetime, BaseModel, ConfigDict
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import DateTime, TypeDecorator


class UTCDateTime(TypeDecorator[datetime]):
    """Store as naive UTC (SQLite drops offsets); load as aware UTC."""

    impl = DateTime
    cache_ok = True

    @override
    def process_bind_param(self, value: datetime | None, dialect: Dialect):
        return value and value.astimezone(UTC).replace(tzinfo=None)

    @override
    def process_result_value(self, value: datetime | None, dialect: Dialect):
        return value and value.replace(tzinfo=UTC)


class Base(DeclarativeBase):
    """Declarative base for every table in the pond."""


class Reading(Base):
    """A temperature reading stored in the pond; one row per sensor per timestamp."""

    __tablename__ = "readings"

    sensor_id: Mapped[str] = mapped_column(primary_key=True)
    ts: Mapped[datetime] = mapped_column(UTCDateTime, primary_key=True)
    temp_c: Mapped[float]


class ReadingPayload(BaseModel):
    """A temperature reading as sent over the wire; naive timestamps are rejected.

    Also used to serialize stored `Reading` rows in API responses.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "sensor_id": "tank1",
                    "ts": "2026-01-01T12:00:00+00:00",
                    "temp_c": 25.0,
                },
            ],
        },
    )

    sensor_id: str
    ts: AwareDatetime
    temp_c: float
