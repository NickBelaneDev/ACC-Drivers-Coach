from src.lap.lap_dataclasses import GForceMetrics
from src.telemetry.telemetry_calculator import TelemetryCalculator
import pandas as pd

from src.lap.dataframe_validation import DataFrameValidator, MissingColumnError, EmptyDataFrameError


class GForceAnalyzer:
    """
    Analyzes the vehicle’s lateral and longitudinal g-forces during a corner.

    The ``GForceAnalyzer`` evaluates both directional (G_LAT, G_LON) and combined
    (gForceVector) acceleration data from a corner-restricted telemetry DataFrame.
    It provides average, min/max, and smoothness-based metrics that describe
    how consistently and efficiently the car generates grip through a corner.

    The results are packaged as a ``GForceMetrics`` dataclass that quantifies the
    balance, stability, and load transfer of the vehicle in physical units (g).
    """
    @staticmethod
    def analyze(df: pd.DataFrame) -> GForceMetrics:
        """
                Compute g-force metrics from a corner telemetry DataFrame.

                This method processes raw g-force telemetry to derive key statistics
                for both lateral and longitudinal acceleration, as well as a combined
                g-force vector. Additionally, it measures smoothness and a total
                “g-force score” based on the integral over distance.

                Parameters
                ----------
                df : pandas.DataFrame
                    The telemetry DataFrame of the analyzed corner. It must include
                    the following columns:
                      - ``"G_LAT"`` : lateral acceleration (g)
                      - ``"G_LON"`` : longitudinal acceleration (g)
                      - ``"gForceVector"`` : resultant combined acceleration (g)
                      - ``"Distance"`` : distance samples for integration

                Returns
                -------
                GForceMetrics
                    A dataclass containing averaged, peak, and smoothness metrics
                    for all g-force components. If the DataFrame is invalid or
                    columns are missing, returns an empty ``GForceMetrics`` object
                    containing the reason for failure.

                Notes
                -----
                - The ``g_force_vector_score`` is computed as the integral of
                  ``gForceVector`` over distance, representing total load transfer.
                - ``g_force_vector_smoothness`` uses the change-rate variance to
                  quantify consistency of applied g-forces — lower variance implies
                  smoother driving dynamics.
                """
        cols = ["G_LAT", "G_LON", "gForceVector", "Distance"]
        try:
            DataFrameValidator.validate_df(df, cols)
        except (MissingColumnError, EmptyDataFrameError) as e:
            return GForceMetrics.empty(reason=str(e))

        # Work on a defensive copy for stable downstream calculations
        g_force_df: pd.DataFrame = df[cols].copy()

        # Extract directional force components
        g_lat_s: pd.Series = df["G_LAT"]
        g_lon_s: pd.Series = df["G_LON"]
        g_force_vector_s: pd.Series = df["gForceVector"]

        # --- Basic statistics (averages and extremes)
        g_lat_avg: float = g_lat_s.mean()
        g_lat_max: float = g_lat_s.max()
        g_lat_min: float = g_lat_s.min()
        g_lon_avg: float = g_lon_s.mean()
        g_lon_max: float = g_lon_s.max()
        g_lon_min: float = g_lon_s.min()

        g_force_vector_avg: float = g_force_vector_s.mean()
        g_force_vector_min: float = g_force_vector_s.min()
        g_force_vector_max: float = g_force_vector_s.max()

        # --- Dynamic metrics
        # Smoothness describes the variance of change rate in g-force magnitude
        g_force_vector_smoothness: float = round(1 / max(TelemetryCalculator.change_rate_var(g_force_df, "gForceVector"), 1e-6),
                                                 4)
        g_force_vector_score: float = round(TelemetryCalculator.get_integral(g_force_df, "gForceVector"),
                                            4)

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
