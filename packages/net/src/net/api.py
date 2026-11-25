"""FastAPI service that catches readings from the bobbers and serves them on."""

from collections.abc import AsyncGenerator, Iterator, Sequence
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Query, Request
from pydantic import AwareDatetime
from sqlalchemy.orm import Session

from net import paths
from net.pond import db
from net.pond.models import Reading, ReadingPayload


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Open the pond when the service starts and close it when it stops."""
    path = paths.db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    app.state.engine = db.open_engine(path)
    yield
    app.state.engine.dispose()


def get_session(request: Request) -> Iterator[Session]:
    """Provide a database session for the duration of one request."""
    with Session(request.app.state.engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(title="net", lifespan=lifespan)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Report that the service is up."""
    return {"status": "ok"}


@app.post("/readings", status_code=201, tags=["readings"])
def ingest(reading: ReadingPayload, session: SessionDep) -> None:
    """Store a reading sent by a bobber."""
    db.insert_reading(session, reading)


@app.get("/readings/latest", response_model=list[ReadingPayload], tags=["readings"])
def latest(session: SessionDep) -> Sequence[Reading]:
    """Return the most recent reading for each sensor."""
    return db.latest_readings(session)


@app.get("/readings", response_model=list[ReadingPayload], tags=["readings"])
def readings(
    session: SessionDep,
    sensor_id: str | None = None,
    since: AwareDatetime | None = None,
    limit: Annotated[int, Query(ge=1, le=10_000)] = 1000,
) -> Sequence[Reading]:
    """Return readings newest-first, optionally filtered by sensor and start time."""
    return db.recent_readings(session, sensor_id, since, limit)
