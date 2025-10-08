from src.lap.lap_model import LapModel

from src.lap.lap_dataclasses import Corner, CornerMetrics, SegmentMetrics, Segment
from pathlib import Path
import os
import pandas as pd
import pprint

from src.telemetry.telemetry_loader import TelemetryLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
def load_all_files(base_dir:Path=PROJECT_ROOT, track:str="spa"):
    p = base_dir / "assets" / "MoTeC" / track.lower()
    csv_files: list[Path] = list(p.glob("**\*.csv"))

    all_files_df: pd.DataFrame = pd.DataFrame()

    for f in csv_files:
        raw_lap_df = TelemetryLoader(base_dir)

load_all_files()

