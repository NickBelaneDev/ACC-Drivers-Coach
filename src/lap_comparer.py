import pandas as pd
import numpy as np
from lap_dataclasses import Corner, CornerMetrics, Segment
from src.lap_analyzer import LapAnalyzer

from src.telemetry_utils import get_corner_df_from_df, get_segment_df_from_lap_fd


# LapCompare bekommt zwei DFs der ganzen Lap und vergleicht die Analysedaten der Kurven und Segmente.
#
# Was für Werte wollen wir haben?
#
# 1.) TelemetryLoader


class LapCompare:

    def __init__(self, lap_df: pd.DataFrame):
        self.lap_df = LapAnalyzer.calc_g_force_vector(lap_df)
        self.analyze = LapAnalyzer(self.lap_df)


    def load_segments_df(self, _lap_df: pd.DataFrame=None) -> pd.DataFrame:
        lap_df = self.lap_df
        if _lap_df is not None:
            lap_df = _lap_df

        cols = ["timeDelta",
                "start_m",
                "end_m",
                "totalDistance",
                "avgThrottle",
                "avgBreak",
                "avgSpeed",
                "topSpeed",
                "minSpeed",
                "avgGForceVector"]
        segment_df = pd.DataFrame(columns=cols)

        rows = []

        for _id in sorted(lap_df["segment_id_x"].unique()):
            _segment_df = get_segment_df_from_lap_fd(_id, lap_df)
            segment_end = _segment_df["segmentEnd_m"].iloc[0]
            segment_start = _segment_df["segmentStart_m"].iloc[0]
            time_delta = _segment_df["Time"].iloc[-1] - _segment_df["Time"].iloc[0]

            row = {
                    "timeDelta": time_delta,
                    "start_m": segment_start,
                    "end_m": segment_end,
                    "totalDistance": segment_end - segment_start,
                    "avgThrottle": _segment_df["THROTTLE"].mean(),
                    "avgBreak": _segment_df["BRAKE"].mean(),
                    "avgSpeed": _segment_df["SPEED"].mean(),
                    "topSpeed": _segment_df["SPEED"].max(),
                    "minSpeed": _segment_df["SPEED"].min(),
                    "avgGForceVector": _segment_df["gForceVector"].mean()
                }

            rows.append(row)
        segment_df = pd.DataFrame(rows, columns=cols).sort_values("start_m").reset_index(drop=True)
        return segment_df

    def _load_corners(self, df: pd.DataFrame, ):


        pass

    def get_comparison_df(self, df):
        pass

    def get_comparison_json(self, df):
        pass