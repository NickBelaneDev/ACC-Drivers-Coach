import pandas as pd
import math
from src.telemetry.telemetry_calculator import TelemetryCalculator
from ..lap_dataclasses import SteerMetrics
from ..dataframe_validation import DataFrameValidator, DataFrameColumnError

class SteerAnalyzer:
    @staticmethod
    def analyze(df: pd.DataFrame=None) -> SteerMetrics:
        cols = ["STEERANGLE", "ROTY", "Distance"]
        try:
            DataFrameValidator.check_has_cols(df, cols) # Returnt True oder raise DataFrameColumnError
        except DataFrameColumnError as er:
            return SteerMetrics.empty(reason=str(er))

        avg_steerangle = df["STEERANGLE"].mean()
        max_steerangle = df["STEERANGLE"].max()
        max_steerangle_m = df.loc[df["STEERANGLE"].idxmin(), "Distance"]
        steering_integral = TelemetryCalculator.get_integral(df, "STEERANGLE", amplitude_mode=True)
        steering_smoothness = TelemetryCalculator.change_rate_var(df, "STEERANGLE")

        rotation_integral = TelemetryCalculator.get_integral(df, "ROTY", amplitude_mode=False)
        rotation_smoothness = TelemetryCalculator.change_rate_var(df, "ROTY")

        return SteerMetrics(
            avg_steerangle=avg_steerangle, max_steerangle=max_steerangle,
            max_steerangle_m=max_steerangle_m, steering_smoothness=steering_smoothness,
            steering_integral=steering_integral, rotation_integral=rotation_integral,
            rotation_smoothness=rotation_smoothness
        )

