"""Streamlit dashboard: net's health, the latest readings, and temperature history."""

import os
from dataclasses import asdict
from datetime import UTC, datetime, timedelta

import httpx
import pandas as pd
import plotly.express as px
import streamlit as st

from fisherman import client

NET_URL = os.environ.get("FISHERMAN_NET_URL", "http://localhost:8000")
HISTORY = timedelta(hours=24)

st.set_page_config(page_title="Fisherman", page_icon=":material/set_meal:")
st.title("Fisherman")


@st.fragment(run_every="10s")
def health_badge() -> None:
    """Show whether net is reachable, re-checking every 10 seconds."""
    if client.is_healthy(NET_URL):
        st.badge("net is up", icon=":material/check_circle:", color="green")
    else:
        st.badge(
            f"net is unreachable at {NET_URL}",
            icon=":material/error:",
            color="red",
        )


health_badge()


def to_frame(readings: list[client.Reading]) -> pd.DataFrame:
    """Turn readings into a dataframe with columns sensor_id, ts, temp_c."""
    columns = ["sensor_id", "ts", "temp_c"]
    return pd.DataFrame([asdict(r) for r in readings], columns=columns)


@st.cache_data(ttl="30s")
def load_latest() -> pd.DataFrame:
    """Fetch the newest reading per sensor."""
    return to_frame(client.latest_readings(NET_URL))


@st.cache_data(ttl="30s")
def load_history() -> pd.DataFrame:
    """Fetch every reading from the last `HISTORY`, oldest first for plotting."""
    since = datetime.now(UTC) - HISTORY
    frame = to_frame(client.readings_since(NET_URL, since))
    return frame.sort_values("ts")


try:
    latest = load_latest()
    history = load_history()
except httpx.HTTPError as error:
    st.error(f"Could not load readings from {NET_URL}: {error}", title="No data")
    st.stop()

if latest.empty:
    st.info("Start a bobber or seed the database to see data.", title="No readings yet")
    st.stop()

# Show times in the viewer's timezone (reported by their browser).
tz = st.context.timezone or "UTC"
latest["ts"] = latest["ts"].dt.tz_convert(tz)
history["ts"] = history["ts"].dt.tz_convert(tz)

with st.container(border=True):
    st.subheader("Latest readings")
    st.dataframe(
        latest.sort_values("sensor_id"),
        hide_index=True,
        column_config={
            "sensor_id": st.column_config.TextColumn("Sensor"),
            "ts": st.column_config.DatetimeColumn("Last reading", format="distance"),
            "temp_c": st.column_config.NumberColumn("Temperature", format="%.1f °C"),
        },
        alt="Most recent temperature reported by each sensor",
    )

with st.container(border=True):
    st.subheader("Temperature, last 24 hours")
    figure = px.line(
        history,
        x="ts",
        y="temp_c",
        color="sensor_id",
        labels={"ts": "Time", "temp_c": "Temperature (°C)", "sensor_id": "Sensor"},
    )
    st.plotly_chart(figure, alt="Temperature over the last 24 hours, by sensor")
