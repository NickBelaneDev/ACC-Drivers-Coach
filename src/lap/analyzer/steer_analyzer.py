import pandas as pd
from src.telemetry.telemetry_calculator import TelemetryCalculator
from ..lap_dataclasses import SteerMetrics
from src.lap.dataframe_validation import DataFrameValidator, MissingColumnError


class SteerAnalyzer:
    """
    Analyzes steering behavior and its dynamic influence on the vehicle.

    The ``SteerAnalyzer`` evaluates steering-related telemetry data to quantify
    how the driver inputs steering throughout a corner and how the car reacts to it.
    It provides metrics for average and peak steering angles, steering smoothness,
    and rotational response (ROTY), allowing detailed insight into driver control,
    steering balance, and vehicle rotation dynamics.

    The results are returned as a ``SteerMetrics`` dataclass, which aggregates all
    steering-related KPIs for integration into higher-level driver and car analyses.
    """
    @staticmethod
    def analyze(df: pd.DataFrame) -> SteerMetrics:
        """
        Compute steering and rotation metrics from a telemetry DataFrame.

        This method processes a subset of steering-related signals from the raw telemetry.
        It calculates statistical and dynamic measures that characterize both driver input
        (steering angle) and vehicle response (rotation rate). Additionally, it measures
        smoothness and total input amplitude through integrals and rate variance.

        Parameters
        ----------
        df : pandas.DataFrame
            Telemetry data of the current corner. Must contain:
            ``["STEERANGLE", "BRAKE", "THROTTLE", "ROTY", "Distance"]``.

        Returns
        -------
        SteerMetrics
            Dataclass with metrics describing steering behavior and rotation dynamics.
            Returns an empty ``SteerMetrics`` instance if validation fails or data is missing.

        Notes
        -----
        - ``steering_integral`` quantifies the overall steering effort across the corner.
        - ``steering_smoothness`` reflects the variance in steering rate change;
          lower values indicate more consistent, precise input.
        - ``rotation_integral`` and ``rotation_smoothness`` measure how the vehicle rotates
          in response to the steering input, based on the ``ROTY`` (yaw rate) signal.
        """
        cols = ["STEERANGLE", "BRAKE", "THROTTLE", "ROTY", "Distance"]
        try:
            DataFrameValidator.validate_df(df, cols) # Returns True or raises DataFrameColumnError
        except MissingColumnError as er:
            return SteerMetrics.empty(reason=str(er))

        steer_s: pd.Series = df["STEERANGLE"]
        steer_df: pd.DataFrame = df[cols].copy()

        # --- Steering input statistics
        avg_steerangle: float = steer_s.mean()
        max_steerangle: float = steer_s.max()
        max_steerangle_m: float = steer_df.loc[steer_df["STEERANGLE"].idxmax(), "Distance"] # Distance at max steering angle

        # --- Steering smoothness and overall input amplitude
        steering_integral: float = TelemetryCalculator.get_integral(steer_df, "STEERANGLE", amplitude_mode=True)
        steering_smoothness: float = TelemetryCalculator.change_rate_var(steer_df, "STEERANGLE")

        # --- Vehicle rotation response (ROTY)
        max_rotation: float = steer_df["ROTY"].max()
        rotation_integral: float = TelemetryCalculator.get_integral(steer_df, "ROTY", amplitude_mode=False)
        rotation_smoothness: float = TelemetryCalculator.change_rate_var(steer_df, "ROTY")

        """
        # Future extension:
        # Analyze steering–braking overlap or excessive steering under throttle/brake.
        # TODO: implement advanced steering interaction metrics.
        """

        return SteerMetrics(
            avg_steerangle=avg_steerangle,
            max_steerangle=max_steerangle,
            max_steerangle_m=max_steerangle_m,
            steering_smoothness=steering_smoothness,
            steering_integral=steering_integral,
            max_rotation=max_rotation,
            rotation_integral=rotation_integral,
            rotation_smoothness=rotation_smoothness
        )

