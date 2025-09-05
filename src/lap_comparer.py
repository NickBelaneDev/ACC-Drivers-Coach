import pandas as pd
import numpy as np
from lap_dataclasses import Corner, CornerMetrics, Segment
from src.lap_analyzer import LapAnalyzer

from src.telemetry_utils import get_corner_df_from_df


# LapCompare bekommt zwei DFs der ganzen Lap und vergleicht die Analysedaten der Kurven und Segmente.
#
# Was für Werte wollen wir haben?
#
# 1.) TelemetryLoader


class LapCompare:

    def __init__(self, lap_df: pd.DataFrame):
        self.lap_df = LapAnalyzer.calc_g_force_vector(lap_df)
        self.analyze = LapAnalyzer(self.lap_df)


    def _load_segments(self, _lap_df=None) -> pd.DataFrame:
        lap_df = self.lap_df
        if _lap_df:
            lap_df = _lap_df

        _n_segments = lap_df["segment_id_x"].max()
        _segment_ids = set(lap_df["segment_id_x"])

        _columns = ["Test"]

        segment_data = {
            "metrics": {
                "avgThrottle": lap_df["THROTTLE"].mean(),
                "avgBreak": lap_df["BRAKE"].mean(),
                "avgSpeed": lap_df["SPEED"].mean(),
                "topSpeed": lap_df["SPEED"].max(),
                "minSpeed": lap_df["SPEED"].min(),
                "maxGForceVector": lap_df["gForceVector"].mean(),
                "timeDelta": time_delta
            },

            "geo": {
                "start_m": segment_start,
                "end_m": segment_end,
                "totalDistance": segment_end - segment_start
            }}

        segments = pd.DataFrame(columns=_columns)

        for n in range(1, _n_segments + 1):
            pass



    def _load_corners(self, df: pd.DataFrame, ):


        pass

    def get_comparison_df(self, df):
        pass

    def get_comparison_json(self, df):
        pass