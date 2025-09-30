import pandas as pd
import numpy as np
from dataclasses import asdict
from src.telemetry.telemetry_calculator import TelemetryCalculator
from src.telemetry.telemetry_utils import get_df_from_area
from src.lap.lap_dataclasses import ThrottleMetrics
from src.logger import get_logger

log = get_logger("ThrottleAnalysis", level="DEBUG", to_console=True)

class ThrottleAnalysis:
    def __init__(self):
        pass

    @staticmethod
    def get_throttle_data(df:pd.DataFrame, threshold:int=0) -> ThrottleMetrics:
        """
        :param df: pd.DataFrame of the area you want to analyze. Typically, it is the corner area defined in the corresponding [map]corner.json file.
        :param threshold: threshold for throttle detection.
        :return:
        """

        # validate the DataFrame & determine the needed cols
        def _validate_df(to_validate_df:pd.DataFrame, cols:list[str]) -> pd.DataFrame:

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
            return validated_df

        _cols = ["THROTTLE", "Distance", "Time"]

        try:
            throttle_df = _validate_df(df, _cols)
        except ValueError as v:
            return ThrottleMetrics.empty(reason=str(v))


        # Determine the acceleration window of the DataFrame
        # This is the part, where the driver is accelerating out of the corner.
        was_not_accelerating = throttle_df["THROTTLE"].shift(1).fillna(0) <= threshold
        is_accelerating = throttle_df["THROTTLE"] > threshold
        acceleration_window_df: pd.DataFrame = throttle_df[is_accelerating & was_not_accelerating]
        acceleration_rate: float = TelemetryCalculator.average_change_rate(acceleration_window_df, "THROTTLE")
        acceleration_delta_m: float = acceleration_window_df["Distance"].max() - acceleration_window_df["Distance"].min()
        acceleration_delta_s: float = acceleration_window_df["Time"].max() - acceleration_window_df["Time"].min()

        # Basic telemetry information
        avg_throttle: float = round(throttle_df[throttle_df["THROTTLE"] > 0]["THROTTLE"].mean(), 4)
        min_throttle: float = round(throttle_df["THROTTLE"].min(), 4)
        max_throttle: float = round(throttle_df["THROTTLE"].max(), 4)
        min_throttle_m: float = throttle_df.loc[min_throttle]["Distance"]
        max_throttle_m: float = throttle_df.loc[max_throttle]["Distance"]

        # Detailed Exit-Throttle Analysis
        integral: float = round(TelemetryCalculator.get_integral(acceleration_window_df, "THROTTLE", "Distance"), 4)
        exit_throttle_init_m: float = acceleration_window_df["Distance"].min()  #throttle_df[(throttle_df["THROTTLE"] > threshold) & (throttle_df["THROTTLE"].shift(1) <= 0)].min()

        ttf95: float =  throttle_df[throttle_df["THROTTLE"] >= 95]["Time"].max() - throttle_df[throttle_df["THROTTLE"] >= 95]["Time"].min()
        throttle_smoothness: float = 1 / min(TelemetryCalculator.parameter_stability(acceleration_window_df, "THROTTLE", amplitude_mode=True), 1e-6)


        return ThrottleMetrics(
            avg_throttle=avg_throttle, min_throttle_m=min_throttle_m, min_throttle=min_throttle, max_throttle_m=max_throttle_m,
            max_throttle=max_throttle, integral=integral, exit_throttle_init_m=exit_throttle_init_m, ttf95=ttf95, throttle_smoothness=throttle_smoothness,
            acceleration_delta_m=acceleration_delta_m, acceleration_delta_s=acceleration_delta_s, acceleration_rate=acceleration_rate
        )