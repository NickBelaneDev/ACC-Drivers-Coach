import pandas as pd
import numpy as np
from lap_dataclasses import Corner, CornerMetrics, Segment
from src.lap_analyzer import LapAnalyzer

from src.telemetry_utils import get_corner_df_from_df, get_segment_df_from_lap_fd, segment_to_df
from logger import get_logger

# LapCompare bekommt zwei DFs der ganzen Lap und vergleicht die Analysedaten der Kurven und Segmente.
#
# Was für Werte wollen wir haben?
#
# 1.) TelemetryLoader

log = get_logger(to_console=False)
class LapCompare:

    def __init__(self, lap_df: pd.DataFrame):
        self.lap_df = LapAnalyzer.calc_g_force_vector(lap_df)
        self.analyze = LapAnalyzer(self.lap_df)


    def new_lap(self, lap_df):
        self.lap_df = self.analyze.calc_g_force_vector(lap_df)
        return self.lap_df

    def load_segments_df(self, _lap_df:pd.DataFrame=None) -> pd.DataFrame:
        lap_df = self.lap_df
        if _lap_df is not None:

            lap_df: pd.DataFrame = self.new_lap(_lap_df)
            log.debug(f"{lap_df.info()=}")

        segments = []
        # Filling all the rows
        for _id in sorted(lap_df["segment_id_x"].dropna().unique()):
            _segment_df = get_segment_df_from_lap_fd(_id, lap_df)
            _segment, _segment_metrics = self.analyze.segment(_segment_df)

            segment_df = segment_to_df(_segment, _segment_metrics)
            segments.append(segment_df)
            
        return pd.DataFrame([segments])

    def load_corners(self, _lap_df:pd.DataFrame=None):
        lap_df = self.lap_df
        if _lap_df is not None:

            lap_df: pd.DataFrame = self.new_lap(_lap_df)
            log.debug(f"{lap_df.info()=}")

        for _id in sorted(lap_df["corner_id"].dropna().unique()):
            _corner_df = get_corner_df_from_df(_id, lap_df)

        pass

    def get_comparison_df(self, df):
        pass

    def get_comparison_json(self, df):
        pass