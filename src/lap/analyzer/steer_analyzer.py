import pandas as pd
from src.telemetry.telemetry_calculator import TelemetryCalculator
from ..lap_dataclasses import SteerMetrics
from src.lap.dataframe_validation import DataFrameValidator, DataFrameColumnError


class SteerAnalyzer:
    @staticmethod
    def analyze(df: pd.DataFrame) -> SteerMetrics:
        """
        Analyze the steering inputs and its cause to the cars behavior.
        :param df: Raw Telemetry DataFrame
        :return: a dataclass with all information
        """
        cols = ["STEERANGLE", "BRAKE", "THROTTLE", "ROTY", "Distance"]
        try:
            DataFrameValidator.validate_df(df, cols) # Returns True or raises DataFrameColumnError
        except DataFrameColumnError as er:
            return SteerMetrics.empty(reason=str(er))

        steer_s: pd.Series = df["STEERANGLE"]
        steer_df: pd.DataFrame = df[cols].copy()

        avg_steerangle: float = steer_s.mean()
        max_steerangle: float = steer_s.max()
        max_steerangle_m: float = steer_df.loc[steer_df["STEERANGLE"].idxmax(), "Distance"] # Distance at max steering angle

        steering_integral: float = TelemetryCalculator.get_integral(steer_df, "STEERANGLE", amplitude_mode=True)
        steering_smoothness: float = TelemetryCalculator.change_rate_var(steer_df, "STEERANGLE")

        max_rotation: float = steer_df["ROTY"].max()
        rotation_integral: float = TelemetryCalculator.get_integral(steer_df, "ROTY", amplitude_mode=False)
        rotation_smoothness: float = TelemetryCalculator.change_rate_var(steer_df, "ROTY")

        """
        # Hier habe ich aufgehört. Wir implementieren es später, das ist wieder nur Detailarbeit.
        # TODO: Weitermachen!!
        steerangle_threshold: float = 15.0
        brake_threshold: float = 80.0
        is_braking_and_steering_df: pd.DataFrame = steer_df.query("brake_threshold > @brake_threshold and abs(STEERANGLE) > @steerangle_threshold")
        """

        return SteerMetrics(
            avg_steerangle=avg_steerangle, max_steerangle=max_steerangle,
            max_steerangle_m=max_steerangle_m, steering_smoothness=steering_smoothness,
            steering_integral=steering_integral, max_rotation=max_rotation,
            rotation_integral=rotation_integral, rotation_smoothness=rotation_smoothness
        )

