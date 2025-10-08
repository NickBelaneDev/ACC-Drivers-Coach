import pandas as pd
import math
from dataclasses import asdict

from src.lap.dataframe_validation import DataFrameValidator, MissingColumnError, MissingColumnError, \
    EmptyDataFrameError
from src.telemetry.telemetry_calculator import TelemetryCalculator
from src.telemetry.telemetry_utils import get_df_from_area
from src.lap.lap_dataclasses import ThrottleMetrics
from src.logger import get_logger

log = get_logger("ThrottleAnalysis", level="DEBUG", to_console=True)

class ThrottleAnalyzer:
    """
    Analyzer for throttle behavior within a corner window.

    This analyzer extracts driver throttle usage and “acceleration phase” metrics
    from a corner-restricted telemetry DataFrame. It focuses on:
      - overall throttle characteristics (avg/min/max, integral over distance),
      - when acceleration out of the corner begins,
      - how quickly throttle builds (rate, Δm, Δs),
      - smoothness/stability of the throttle ramp,
      - time-to-full (e.g., time to ≥95%).
    """
    def __init__(self):
        """Construct an instance. No state is stored; the class is stateless."""
        pass

    @staticmethod
    def analyze(df:pd.DataFrame, threshold:int=0) -> ThrottleMetrics:
        """
         Compute throttle-related metrics for the provided corner window.

         The method expects a DataFrame restricted to a single corner (i.e., the
         “corner area” defined by your track map JSON). It validates the presence
         of the required columns and then:
           1) Detects the start of the acceleration phase (first transition
              from THROTTLE ≤ threshold to THROTTLE > threshold).
           2) Slices the DataFrame from that point to corner end (acceleration window).
           3) Calculates descriptive statistics (avg/min/max), integral over distance,
              time-to-≥95% throttle (ttf95), smoothness (inverse amplitude variability),
              and ramp characteristics (Δm, Δs, average change rate).

         Parameters
         ----------
         df : pandas.DataFrame
             Telemetry for the corner window; must at least include
             ``["THROTTLE", "Distance", "Time"]``. Missing values are
             treated as 0 for throttle-only computations.
         threshold : int, optional
             Threshold separating “not accelerating” from “accelerating”.
             Defaults to 0 (i.e., any positive throttle counts as accelerating).

         Returns
         -------
         ThrottleMetrics
             A populated dataclass with throttle metrics. If validation fails,
             an empty metrics object (with a reason) is returned.

         Notes
         -----
         - ``ttf95`` is computed over the full corner DataFrame, not just
           the acceleration window, because the driver may reach ≥95% throttle
           later than the first “acceleration” step.
         - ``throttle_smoothness`` uses the inverse of a stability measure; higher
           values indicate a smoother ramp (bounded by a small epsilon).
         """

        # --- Validation: presence of required columns & non-empty frame
        def _validate_df(to_validate_df:pd.DataFrame,
                         cols:list[str])\
                -> pd.DataFrame:
            """Raises a NotImplementedError when called!"""

            if to_validate_df.empty:
                log.error("Empty Dataframe!")
                raise ValueError("DataFrame is empty!")

            # Check if the df contains all cols
            df_cols = to_validate_df.columns
            _has_all_cols = True
            for col in cols:
                if col not in df_cols:
                    _has_all_cols = False
                    #log.error(f"column: {col=} is not in the DataFrame!")
                    raise ValueError(f"column: {col=} is not in the DataFrame!")

            validated_df: pd.DataFrame = to_validate_df[cols].copy() # throttle_df contains the complete injected DataFrame reduced to the needed cols

            log.debug("All columns inside the DataFrame!")
            raise NotImplementedError
            return validated_df

        _cols = ["THROTTLE", "Distance", "Time"]

        try:
            DataFrameValidator.validate_df(df, _cols)
        except (MissingColumnError, EmptyDataFrameError) as v:

            return ThrottleMetrics.empty(reason=str(v))

        throttle_df: pd.DataFrame = df[_cols].fillna(0).copy()

        # --- Acceleration phase detection
        # Define a transition from "not accelerating" → "accelerating"
        was_not_accelerating = throttle_df["THROTTLE"].shift(1) <= threshold
        is_accelerating = throttle_df["THROTTLE"] > threshold

        # Distance at which acceleration begins (if no transition exists, this becomes NaN)
        acceleration_start = throttle_df[is_accelerating & was_not_accelerating]["Distance"].max()

        # Acceleration window: from first acceleration point to the end of the corner
        acceleration_window_df = throttle_df[throttle_df["Distance"] >= acceleration_start]
        #log.debug(f"{acceleration_window_df["Distance"]}")
        #log.debug(f"{acceleration_start=}, {throttle_df["Distance"].iloc[-1]}")

        # --- Ramp characteristics during the acceleration window
        acceleration_rate = TelemetryCalculator.average_change_rate(acceleration_window_df, "THROTTLE")
        acceleration_delta_m: float = acceleration_window_df["Distance"].max() - acceleration_window_df["Distance"].min()
        acceleration_delta_s: float = acceleration_window_df["Time"].max() - acceleration_window_df["Time"].min()

        # --- Descriptive throttle statistics (over full corner window)
        avg_throttle: float = round(throttle_df[throttle_df["THROTTLE"] > 0]["THROTTLE"].mean(), 4)
        min_throttle: float = round(throttle_df["THROTTLE"].min(), 4)
        max_throttle: float = round(throttle_df["THROTTLE"].max(), 4)

        # --- Detailed exit analysis (primarily over acceleration window)
        integral: float = round(TelemetryCalculator.get_integral(acceleration_window_df, "THROTTLE", "Distance"),
                                4)
        exit_throttle_init_m: float = acceleration_window_df["Distance"].min()

        # Time to full(ish) throttle: duration while THROTTLE ≥ 95
        ttf95: float =  (throttle_df[throttle_df["THROTTLE"] >= 95]["Time"].max() -
                         throttle_df[throttle_df["THROTTLE"] >= 95]["Time"].min())

        # Smoothness: inverse amplitude variability; clamp denominator via epsilon
        throttle_smoothness: float = round(1 / max(TelemetryCalculator.parameter_stability(acceleration_window_df, "THROTTLE", amplitude_mode=True), 1e-6),
                                           4)


        return ThrottleMetrics(
            avg_throttle=avg_throttle,
            min_throttle=min_throttle,
            max_throttle=max_throttle,
            integral=integral,
            exit_throttle_init_m=exit_throttle_init_m,
            ttf95=ttf95,
            throttle_smoothness=throttle_smoothness,
            acceleration_delta_m=acceleration_delta_m,
            acceleration_delta_s=acceleration_delta_s,
            acceleration_rate=acceleration_rate
        )