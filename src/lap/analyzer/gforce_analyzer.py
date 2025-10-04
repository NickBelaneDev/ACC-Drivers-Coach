from src.lap.lap_dataclasses import GForceMetrics
from src.telemetry.telemetry_calculator import TelemetryCalculator
import pandas as pd

from src.lap.dataframe_validation import DataFrameValidator, DataFrameColumnError


class GForceAnalyzer:
    @staticmethod
    def analyze(df: pd.DataFrame) -> GForceMetrics:
        cols = ["G_LAT", "G_LON", "gForceVector", "Distance"]
        try:
            DataFrameValidator.validate_df(df, cols)
        except DataFrameColumnError as e:
            return GForceMetrics.empty(reason=str(e))

        g_force_df: pd.DataFrame = df[cols].copy()

        g_lat_s: pd.Series = df["G_LAT"]
        g_lon_s: pd.Series = df["G_LON"]
        g_force_vector_s: pd.Series = df["gForceVector"]

        g_lat_avg: float = g_lat_s.mean()
        g_lat_max: float = g_lat_s.max()
        g_lat_min: float = g_lat_s.min()
        g_lon_avg: float = g_lon_s.mean()
        g_lon_max: float = g_lon_s.max()
        g_lon_min: float = g_lon_s.min()

        g_force_vector_avg: float = g_force_vector_s.mean()
        g_force_vector_min: float = g_force_vector_s.min()
        g_force_vector_max: float = g_force_vector_s.max()

        g_force_vector_smoothness: float = TelemetryCalculator.change_rate_var(g_force_df, "gForceVector")
        g_force_vector_score: float = TelemetryCalculator.get_integral(g_force_df, "gForceVector")

        return GForceMetrics(
            g_lat_avg=g_lat_avg,
            g_lat_max=g_lat_max,
            g_lat_min=g_lat_min,
            g_lon_avg=g_lon_avg,
            g_lon_max=g_lon_max,
            g_lon_min=g_lon_min,
            g_force_vector_avg=g_force_vector_avg,
            g_force_vector_min=g_force_vector_min,
            g_force_vector_max=g_force_vector_max,
            g_force_vector_smoothness=g_force_vector_smoothness,
            g_force_vector_score=g_force_vector_score
        )
