import pandas as pd
import numpy as np
from pandas.io.pytables import dropna_doc

from lap_dataclasses import Corner, CornerMetrics, Segment
from src.lap_analyzer import LapAnalyzer

from src.telemetry_utils import get_corner_df_from_df, get_segment_df_from_lap_fd, segment_to_df, corner_to_df
from logger import get_logger

# LapCompare bekommt zwei DFs der ganzen Lap und vergleicht die Analysedaten der Kurven und Segmente.
#
# Was für Werte wollen wir haben?
#
# 1.) TelemetryLoader

log = get_logger(to_console=False)
class LapCompare:

    def __init__(self, lap_df: pd.DataFrame):
        self.lap_df: pd.DataFrame = LapAnalyzer.calc_g_force_vector(lap_df)
        self.analyze = LapAnalyzer(self.lap_df)


    def set_new_lap(self, lap_df):
        self.lap_df = self.analyze.calc_g_force_vector(lap_df)
        return self.lap_df

    def load_segments_df(self, _lap_df:pd.DataFrame=None) -> pd.DataFrame:
        """Loads and returns a DataFrame consisting of all analyzed segments."""
        lap_df = self.lap_df
        if _lap_df is not None:

            lap_df: pd.DataFrame = self.set_new_lap(_lap_df)
            log.debug(f"{lap_df.info()=}")

        segments = []
        # Filling all the rows
        for _id in sorted(lap_df["segment_id_x"].dropna().unique()):
            _segment_df = get_segment_df_from_lap_fd(_id, lap_df)
            _segment, _segment_metrics = self.analyze.segment(_segment_df)
            #print(f"{_segment=}")
            segment_df = segment_to_df(_segment, _segment_metrics)

            segments.append(segment_df)
        _final_df = pd.concat(segments, ignore_index=True)

        #print(_final_df)
        return _final_df.fillna(0)

    def load_corners(self, _lap_df:pd.DataFrame=None) -> pd.DataFrame:
        """Loads and returns a DataFrame consisting of all analyzed corners."""
        lap_df = self.lap_df
        if _lap_df is not None:

            lap_df: pd.DataFrame = self.set_new_lap(_lap_df)
            log.debug(f"{lap_df.info()=}")
        corners: list = []
        for _id in sorted(lap_df["corner_id"].dropna().unique()):
            _corner_df = get_corner_df_from_df(_id, lap_df)
            _corner = self.analyze.corner(_corner_df)
            _corner_metrics = _corner.metrics
            corner_df = corner_to_df(_corner, _corner_metrics)
            corners.append(corner_df)

        _final_df = pd.concat(corners, ignore_index=True)

        return _final_df.fillna(0)

    def calc_corner_differences(self, df_1: pd.DataFrame, df_2: pd.DataFrame):
        exclude_cols = ["id", "name", "start_m", "apex_m", "end_m"]

        corner_differences_df = df_1.drop(columns=exclude_cols) - df_2.drop(columns=exclude_cols)
        corner_differences_df = pd.DataFrame.round(corner_differences_df, 2)
        calculated_deltas = pd.concat([df_1[exclude_cols], corner_differences_df], axis=1)
        return calculated_deltas

    def get_comparison_df(self, df):
        pass

    def get_comparison_json(self, df):
        pass