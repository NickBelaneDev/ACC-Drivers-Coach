from pathlib import Path
from typing import List

import streamlit as st
import pandas as pd

from telemetry_loader import TelemetryLoader
from src.lap.lap_telemetry import LapTelemetry


PROJECT_ROOT = Path(__file__).resolve().parent


def _get_tracks() -> List[str]:
    """Return available track names based on folders in assets/MoTec."""
    tracks_dir = PROJECT_ROOT / "assets" / "MoTec"
    return [p.name for p in tracks_dir.iterdir() if p.is_dir()]


def _get_csv_files(track: str) -> List[str]:
    """Return available telemetry csv files for given track."""
    track_dir = PROJECT_ROOT / "assets" / "MoTec" / track
    return [p.name for p in track_dir.glob("*.csv")]


@st.cache_data
def load_lap(track: str, csv_file: str) -> pd.DataFrame:
    """Load telemetry for track and csv file and return processed dataframe."""
    loader = TelemetryLoader(base_dir=PROJECT_ROOT)
    df = loader.telemetry_from_csv(f"assets/MoTec/{track}/{csv_file}", track)
    lap = LapTelemetry(df)
    return lap.lap_df


def main() -> None:
    st.title("Lap Telemetry Viewer")

    tracks = _get_tracks()
    track = st.sidebar.selectbox("Track", tracks)

    csv_files = _get_csv_files(track)
    csv_file = st.sidebar.selectbox("Telemetry file", csv_files)

    lap_df = load_lap(track, csv_file)

    segment_ids = sorted(lap_df["segment_id_x"].dropna().unique().astype(int).tolist())
    segment_option = st.sidebar.selectbox("Segment", ["All"] + segment_ids)
    seg_df = lap_df if segment_option == "All" else lap_df[lap_df["segment_id_x"] == segment_option]

    corner_ids = sorted(seg_df["corner_id"].dropna().unique().astype(int).tolist())
    corner_option = st.sidebar.selectbox("Corner", ["All"] + corner_ids)
    data_df = seg_df if corner_option == "All" else seg_df[seg_df["corner_id"] == corner_option]

    st.subheader("Telemetry")
    st.line_chart(data_df.set_index("Distance")[["SPEED", "THROTTLE", "BRAKE", "gForceVector"]])


if __name__ == "__main__":
    main()
