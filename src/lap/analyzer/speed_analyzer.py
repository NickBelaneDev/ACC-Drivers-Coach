import pandas as pd
import math

from src.lap.dataframe_validation import DataFrameValidator, MissingColumnError, EmptyDataFrameError
from ..lap_dataclasses import SpeedMetrics
from ...telemetry.telemetry_calculator import TelemetryCalculator
from ...logger import get_logger

log = get_logger("SpeedAnalyzer", to_console=False, log_file="src/lap/analyzer/log/speed_analyzer.log")

class SpeedAnalyzer:
    """
    Analyzes the vehicle’s speed behavior through a corner.

    The ``SpeedAnalyzer`` computes speed-related metrics from a telemetry DataFrame
    restricted to a single corner. It extracts characteristic speed values (entry, apex,
    and exit), as well as overall statistical and dynamic properties of the car’s motion.

    Core measurements include:
      - entry, apex, and exit speed (km/h),
      - average, minimum, and maximum corner speed,
      - distance of the minimum-speed point,
      - acceleration and deceleration rates across respective segments.

    The results are returned as a ``SpeedMetrics`` dataclass that provides a compact,
    validated summary for integration into higher-level telemetry or performance analysis.
    """
    @staticmethod
    def analyze(df: pd.DataFrame) -> SpeedMetrics:
        """
        Compute all speed-based metrics for a corner telemetry DataFrame.

        This method validates the input data, identifies key corner positions
        (start, apex, end), and calculates both static and dynamic indicators of
        vehicle speed behavior throughout the corner.

        Parameters
        ----------
        df : pandas.DataFrame
            Telemetry data for the current corner. Must include the columns:
            ``["SPEED", "Distance", "cornerStart_m", "cornerApex_m", "cornerEnd_m"]``.

        Returns
        -------
        SpeedMetrics
            A populated dataclass with all speed metrics. If validation fails or
            required columns are missing, an empty ``SpeedMetrics`` instance is returned.

        Notes
        -----
        - Entry, apex, and exit speeds are derived by finding the nearest recorded
          distances to the defined corner points.
        - Acceleration and deceleration rates are calculated via the
          ``TelemetryCalculator.average_change_rate()`` method over respective
          monotonic regions of the speed curve.
        - Empty sub-windows (e.g., when no pure acceleration phase exists) yield NaN rates.
        """
        cols = ["SPEED", "Distance", "cornerStart_m", "cornerApex_m", "cornerEnd_m"]

        try:
            DataFrameValidator.validate_df(df, cols)
        except MissingColumnError as d_c_e:
            return SpeedMetrics.empty(reason=str(d_c_e))
        except EmptyDataFrameError as e_d_e:
            return SpeedMetrics.empty(reason=str(e_d_e))

        # Refine the DataFrame and ensure distance-based sorting
        speed_df:pd.DataFrame = df[cols].sort_values(by="Distance").copy()

        speed_s: pd.Series = speed_df["SPEED"].copy()
        entry_point: int = df["cornerStart_m"].min()
        apex_point: int = df["cornerApex_m"].min()
        end_point: int = df["cornerEnd_m"].min()

        # Locate speed values closest to the defined geometric reference points
        entry_idx = (speed_df["Distance"] - entry_point).abs().idxmin()
        entry_speed_kmh: float = speed_df.loc[entry_idx, "SPEED"]

        apex_idx = (speed_df["Distance"] - apex_point).abs().idxmin()
        apex_speed_kmh: float = speed_df.loc[apex_idx, "SPEED"]

        exit_idx = (speed_df["Distance"] - end_point).abs().idxmin()
        exit_speed_kmh: float = speed_df.loc[exit_idx, "SPEED"]

        # Aggregate statistical descriptors
        avg_speed_kmh: float = speed_s.mean()
        max_speed_kmh: float = speed_s.max()
        min_speed_kmh: float = speed_s.min()
        min_speed_m: float = speed_df.loc[speed_df["SPEED"].idxmin(), "Distance"]

        # Derive acceleration/deceleration characteristics
        deceleration_window: pd.DataFrame = speed_df[speed_df["SPEED"] < speed_df["SPEED"].shift()]
        deceleration_rate: float = (
            TelemetryCalculator.average_change_rate(deceleration_window, "SPEED")
            if not deceleration_window.empty
            else math.nan
        )

        acceleration_window: pd.DataFrame = speed_df[speed_df["SPEED"] > speed_df["SPEED"].shift()]
        acceleration_rate: float = (
            TelemetryCalculator.average_change_rate(acceleration_window, "SPEED")
            if not acceleration_window.empty
            else math.nan
        )
        log.info("Successfully created all data for SpeedMetrics!")
        return SpeedMetrics(
            entry_speed_kmh=entry_speed_kmh,
            apex_speed_kmh=apex_speed_kmh,
            exit_speed_kmh=exit_speed_kmh,
            avg_speed_kmh=avg_speed_kmh,
            max_speed_kmh=max_speed_kmh,
            min_speed_kmh=min_speed_kmh,
            min_speed_m=min_speed_m,
            deceleration_rate=deceleration_rate,
            acceleration_rate=acceleration_rate
        )